#!/usr/bin/env python
# coding: utf-8
"""
Created On Jul 2, 2014

@author: jwang
"""
import re
import logging
import simplejson

# from django.conf import settings
# from django.views.decorators.http import require_GET, require_POST
from weibonews.utils.web.decorators import json_response, perf_logging
from weibonews.utils.format import timestamp_now
# from weibonews.utils.web.errors import parameter_error
from wechat.utils import get_parameter
from wechat.service.decorators import catch_except
from wechat.service.models import wechatdb

_LOGGER = logging.getLogger('weibonews.wechat')

_VOTE_FLAG_RE = re.compile(r'(strong|weak)')

ROBOT = u'投票小助手'
ROBOT_IDS = ['dolphinvote', 'wxid_6gjnt8hc8ctk22']

_CONFIG_WEIGHT_RE = re.compile(ur'顶占(\d+)%通过')
_CONFIG_NOT_VOTE_RE = re.compile(ur'统计未投票人员.*(是|否)')
_SHORTCUT_RE = re.compile(ur'%s(\s|\u2005)(\d+)\s?(.*)' % ROBOT)



START = u'开始投票'
STRONG = u'strong'
WEAK = u'weak'
END = u'完成投票'
SEARCH = u'查询'
CONFIG = u'配置'
START_FLAG = u'请为'
SPLIT_FLAG = u'和'
END_FLAG = u'开始投票'
YES = u'是'
PASSED_MAP = {
    True: u'通过',
    False: u'未通过'
}
HELP = u'开始单项投票格式: @%s 请为XXX开始投票.\n多项投票: @%s 请为XX和XX开始投票.\n结束投票: @%s 完成投票.\n配置投票获取帮助格式: @%s 配置.\n查询格式: @%s 查询@XXX.' \
        % (ROBOT, ROBOT, ROBOT, ROBOT, ROBOT)
CONFIG_HELP = u'配置格式: @%s 配置顶占xx%%通过，统计未投票人员:是|否' % ROBOT


class Status(object):
    '''Vote task status'''
    START = 0
    FINISHED = 2


@json_response
@catch_except
@perf_logging
def handler(request):
    '''
    vote process method
    '''
    group_id = get_parameter(request, 'group_id', required=True, method="POST")
    msg = get_parameter(request, 'msg', required=True, method="POST")
    sender = get_parameter(request, 'sender', required=True, method="POST")
    nick = get_parameter(request, 'nick', required=True, method="POST")
    member = get_parameter(request, 'member', default=None, method="POST")
    group_users = get_parameter(request, 'group_users', default=None, method="POST")
    voted = get_parameter(request, 'voted', default=None, method="POST")
    _LOGGER.info(msg)
    _LOGGER.info(u'member: %s' % member)
    convert = shortcut(msg)
    _LOGGER.info(convert)
    if convert:
        msg = convert
        _LOGGER.info(msg)
    for key in PROCESS_MAP:
        if key in msg:
            if key == END:
                return PROCESS_MAP[key](group_id, sender, nick, msg, group_users)
            elif key == SEARCH:
                return PROCESS_MAP[key](group_id, member, nick, msg)
            elif key == START:
                tip_dict = PROCESS_MAP[key](group_id, sender, nick, msg, voted)
                return {'tip': u'%s\n%s' % (convert, tip_dict['tip'])}
            else:
                return PROCESS_MAP[key](group_id, sender, nick, msg)
    return {'tip': HELP}


def shortcut(msg):
    '''convert shortcut to normal msg'''
    msg = msg[1:]
    result = u''
    match_sc = _SHORTCUT_RE.search(msg)
    if match_sc:
        shortcut_number = match_sc.group(2)
        if shortcut_number == '0':
            result = u'完成投票'
        elif shortcut_number == '1':
            voted = match_sc.group(3)
            voted = voted.strip()
            if voted:
                result = u'请为%s的工作汇报开始投票' % voted
        elif shortcut_number == '2':
            voted = match_sc.group(3)
            voted = voted.strip()
            if voted:
                result = u'请为%s的文档准备和汇报演讲开始投票' % voted
    return result


def vote_config(group_id, starter, nick, msg):
    '''
    vote config
    '''
    tip = ''
    group_config = {
        'group_id': group_id,
        'created': timestamp_now()
    }
    match_weight = _CONFIG_WEIGHT_RE.search(msg)
    if match_weight:
        weight = match_weight.group(1)
        weight = int(weight) * 1.0 / 100
        group_config['weight'] = weight
        tip = u'配置权重成功'
    _LOGGER.info(msg)
    match_not_vote = _CONFIG_NOT_VOTE_RE.search(msg)
    if match_not_vote:
        not_vote = match_not_vote.group(1)
        if not_vote == YES:
            not_vote = True
        else:
            not_vote = False
        group_config['not_vote'] = not_vote
        if tip:
            tip = u'配置权重和未投票人员统计成功'
        else:
            tip = u'配置未投票人员统计成功'
    if 'weight' in group_config or 'not_vote' in group_config:
        wechatdb.update_group_config({'group_id': group_id}, group_config, upsert=True)
    if not tip:
        tip = CONFIG_HELP
    return {'tip': tip}


def vote_start(group_id, starter, nick, msg, voted):
    '''
    vote start
    '''
    tip = u'------\n我是开始投票分割线\n顶[强]\n踩[弱]\n------'
    vote_id = wechatdb.get_vote_by_group(group_id)
    if vote_id:
        tip = u'本群有一个未结束的投票 将被覆盖 现在开始新的投票'
    if START_FLAG in msg:
        items_str = msg.split(START_FLAG)[1]
        if END_FLAG in items_str:
            items_str = items_str.split(END_FLAG)[0]
            items = items_str.split(SPLIT_FLAG)
            vote_id = wechatdb.next_id('vote')
            vote_group = {
                'group_id': group_id,
                'vote_id': vote_id,
            }
            wechatdb.update_vote_group({'group_id': group_id}, vote_group, upsert=True)
            vote_task = {
                    'id': vote_id,
                    'weight': 0.5,
                    'not_vote': True,
                    'group_id': group_id,
                    'start_msg': msg,
                    'starter': starter,
                    'nick': nick,
                    'voted': voted,
                    'created': timestamp_now(),
                    'status': Status.START,
                    'items': items,
                }
            group_config = wechatdb.get_group_config({'group_id': group_id})
            if group_config:
                if 'weight' in group_config:
                    vote_task['weight'] = group_config['weight']
                if 'not_vote' in group_config:
                    vote_task['not_vote'] = group_config['not_vote']
            wechatdb.update_vote_task({'id': vote_id}, vote_task, upsert=True)
        else:
            tip = HELP
    else:
        tip = HELP
    return {'tip': tip}

def voting(group_id, voter, nick, msg):
    '''
    voting
    '''
    tip = ''
    vote_id = wechatdb.get_vote_by_group(group_id)
    if vote_id:
        vote_values = _VOTE_FLAG_RE.findall(msg)
        task = wechatdb.get_vote_task({'id': vote_id})
        item_number = len(task['items'])
        record_id = wechatdb.next_id('vote_record')
        vote_record = {
            'id': record_id,
            'vote_id': vote_id,
            'vote': vote_values,
            'group_id': group_id,
            'msg': msg,
            'voter': voter,
            'nick': nick,
            'created': timestamp_now(),
        }
        if item_number == len(vote_values):
            vote_record['valid'] = True
        else:
            vote_record['valid'] = False
        wechatdb.update_vote_record({'vote_id': vote_id, 'voter': voter}, vote_record, upsert=True)
        wechatdb.update_vote_task({'id': vote_id}, {'$set': {'last_voter': nick}})
    return {'tip': tip}

def vote_finish(group_id, sender, nick, msg, group_users):
    '''
    vote finished
    '''
    tip = ''
    group_users = simplejson.loads(group_users)
    user_nick = {}
    for user in group_users:
        if user['name'] != ROBOT and user['id'] not in ROBOT_IDS:
            user_nick[user['id']] = user['name']
    vote_id = wechatdb.get_vote_by_group(group_id)
    if vote_id:
        vote_task = wechatdb.get_vote_task({'id': vote_id})
        items = vote_task['items']
        records = wechatdb.get_vote_records({'vote_id': vote_id})
        voter_set = set([record['voter'] for record in records])
        not_vote_users = list(set(user_nick.keys()) - voter_set)
        not_vote_nicks = [user_nick[user] for user in not_vote_users]
        item_results = []
        valid_records = [record for record in records if record['valid']]
        vote_number = len(records)
        vote_valid_number = len(valid_records)
        vote_invalid_number = vote_number - vote_valid_number
        tip = u'总票数: %d\n有效票数: %d\n无效票数: %d' % (vote_number, vote_valid_number, vote_invalid_number)
        if vote_task['voted']:
            tip = u'%s\n%s' % (tip, vote_task['voted'])
        item_tip_list = []
        passed = True
        for i, item in enumerate(items):
            strong_number = len([record for record in valid_records if record['vote'][i] == STRONG])
            weak_number = len([record for record in valid_records if record['vote'][i] == WEAK])
            weight = vote_task['weight']
            passed = passed and (strong_number > (strong_number + weak_number) * weight)
            strong_rate = strong_number * 1.0 / (strong_number + weak_number) if (strong_number + weak_number) > 0 else 0.0
            item_str = u'%s:\n%d%%顶' % (item, strong_rate * 100)
            item_tip_list.append(item_str)

            item_result = {
                'name': item,
                'strong': strong_number,
                'strong_rate': strong_rate,
                'weak': weak_number,
                'passed': passed,
            }
            item_results.append(item_result)
        item_tip = '\n'.join(item_tip_list)
        tip = u'%s\n%s\n投票%s\n最后投票人员: %s\n' % (tip, item_tip, PASSED_MAP[passed], vote_task.get('last_voter', ''))
        if vote_task['not_vote']:
            tip = u'%s未投票人员: %s' % (tip, ','.join(not_vote_nicks) or u'无')

        update = {
            '$set': {
                'not_vote': not_vote_users,
                'finished_time': timestamp_now(),
                'item_results': item_results,
                'status': Status.FINISHED,
                'group_users': user_nick.keys(),
            }
        }
        wechatdb.update_vote_task({'id': vote_id}, update)
        wechatdb.remove_vote_group(group_id)
    else:
        tip = u'投票还未开始'
    return {'tip': tip}

def vote_history(group_id, member, nick, msg):
    '''
    View vote history
    '''
    tip = ''
    vote_tasks = wechatdb.get_vote_tasks({'group_id': group_id, 'group_users': member, 'status': Status.FINISHED})
    if len(vote_tasks) > 0:
        task_ids = [task['id'] for task in vote_tasks]
        vote_records = wechatdb.get_vote_records({'vote_id': {'$in': task_ids}, 'voter': member, 'valid': True})
        record_dict = {}
        for record in vote_records:
            record_dict[record['vote_id']] = record
        strong = 0
        weak = 0
        not_vote = 0
        diff_strong = 0
        diff_weak = 0
        for task in vote_tasks:
            vote_id = task['id']
            if vote_id in record_dict:
                vote_values = record_dict[vote_id]['vote']
                item_results = task['item_results']
                _LOGGER.info(vote_values)
                _LOGGER.info(item_results)
                for vote, item_result in zip(vote_values, item_results):
                    if vote == STRONG:
                        strong += 1
                        if not item_result['passed']:
                            diff_strong += 1
                    else:
                        weak += 1
                        if item_result['passed']:
                            diff_weak += 1
            else:
                not_vote += 1
        _LOGGER.info(diff_weak)
        sum_votes = strong + weak
        strong_rate = 0
        weak_rate = 0
        different_rate = 0
        diff_strong_rate = 0
        diff_weak_rate = 0
        if sum_votes > 0:
            strong_rate = strong * 100.0 / sum_votes
            weak_rate = weak * 100.0 / sum_votes
            different_rate = (diff_strong + diff_weak) * 100.0 / sum_votes
            diff_strong_rate = diff_strong * 100.0 / sum_votes
            diff_weak_rate = diff_weak * 100.0 / sum_votes
        tip = u'查询%s的结果\n顶次数: %d, 占比: %.2f%%\n踩次数: %d, 占比: %.2f%%\n跟结果不同次数: %d, 占比: %.2f%%\n其中顶的次数: %d, 占比: %.2f%%\n踩的次数: %d, 占比: %.2f%%\n未投票次数: %d' % \
                (nick, strong, strong_rate, weak, weak_rate, diff_strong + diff_weak, different_rate, diff_strong, diff_strong_rate, \
                diff_weak, diff_weak_rate, not_vote)
    else:
        tip = u'暂无投票历史'
    return {'tip': tip}


PROCESS_MAP = {
    START: vote_start,
    STRONG: voting,
    WEAK: voting,
    END: vote_finish,
    SEARCH: vote_history,
    CONFIG: vote_config
}
