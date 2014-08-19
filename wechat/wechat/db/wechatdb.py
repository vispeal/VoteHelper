#!/usr/bin/env python
# coding: utf-8
"""
Created On Jul 2, 2014

@author: jwang
"""
import logging
# from pymongo import DESCENDING
from weibonews.utils.decorators import perf_logging
from weibonews.db.utils import cursor_to_array

_LOGGER = logging.getLogger('weibonews.wechat')

DB = None
IDS = None

INDEXES = {
    'vote_records': ['vote_id', 'group_id', 'sender'],
}

PAGE_SIZE = 100


NO_RAW_ID = {
    '_id': 0
}


@perf_logging
def next_id(field):
    """
    Get inc id by field.
    """
    return IDS.next_id(field)

@perf_logging
def update_vote_task(cond, update, upsert=False):
    '''update vote task'''
    DB.vote_tasks.update(cond, update, upsert=upsert)

@perf_logging
def get_vote_task(cond):
    '''get vote task'''
    return DB.vote_tasks.find_one(cond) 

@perf_logging
def get_vote_tasks(cond):
    '''get vote tasks'''
    cursor = DB.vote_tasks.find(cond) 
    return cursor_to_array(cursor)

@perf_logging
def update_vote_record(cond, update, upsert=False):
    '''update vote item'''
    DB.vote_records.update(cond, update, upsert=upsert)

@perf_logging
def get_vote_records(cond):
    '''get vote records'''
    cursor = DB.vote_records.find(cond)
    return cursor_to_array(cursor)

@perf_logging
def update_vote_group(cond, update, upsert=False):
    '''update vote group'''
    DB.vote_groups.update(cond, update, upsert=upsert)

@perf_logging
def get_vote_by_group(group_id):
    '''get vote group'''
    vote_group = DB.vote_groups.find_one({'group_id': group_id})
    if vote_group and 'vote_id' in vote_group:
        return vote_group['vote_id']
    else:
        return None

@perf_logging
def remove_vote_group(group_id):
    '''remove vote group'''
    DB.vote_groups.remove({'group_id': group_id})

@perf_logging
def update_group_config(cond, update, upsert=False):
    '''update group config'''
    DB.group_configs.update(cond, update, upsert=upsert)

@perf_logging
def get_group_config(cond):
    '''get group config'''
    return DB.group_configs.find_one(cond)
