'''
Created on: Dec 20, 2013

@author: qwang
'''
import re
import datetime
import logging

from weibonews.settings import TYPE_MAP
from weibonews.utils.format import timestamp2datetime
from weibonews.utils.decorators import perf_logging
from messagequeue.HandlerRepository import HandlerRepository

_LOGGER = logging.getLogger('weibonews.external')
_handler_repository = HandlerRepository()

_CONTENT_LENGTH_THRESHOLD = 100
_INCOMPLETE_CONTENT_LENGTH_THRESHOLD = 1000
_PUBDATE_INTERVAL = 1 # do not publish if published 1 days ago
_CLEAN_IMG_RE = re.compile("<dolphinimagestart--([0-9a-fA-F]){8}-([0-9a-fA-F]){4}-([0-9a-fA-F]){4}-([0-9a-fA-F]){4}-([0-9a-fA-F]){12}--dolphinimageend>", re.I)

@perf_logging
def _should_publish(info):
    '''
    Should publish the given info, return two value: should_publish and is_content_incomplete
    '''
    info_id = info['_id']
    content_type = info.get('type', None)
    content = None
    if 'news' in info and 'content' in info['news']:
        content = info['news']['content']
    pub_date = info.get('pubDate', None)
    if content is None and pub_date is None:
        # do not filter if content and pub date not provided
        return True, False
    is_content_incomplete = False
    if content_type == TYPE_MAP['news']:
        # check content length, just check for news type
        if not isinstance(content, unicode):
            content = content.encode('utf-8')
        image_count = len(_CLEAN_IMG_RE.findall(content))
        content = _CLEAN_IMG_RE.sub('', content)
        length = len(content)
        is_content_incomplete = image_count == 0 and length < _INCOMPLETE_CONTENT_LENGTH_THRESHOLD
        if length < _CONTENT_LENGTH_THRESHOLD:
            _LOGGER.warn('[PublishAgent] do not publish %s because content too short: %s' % (info_id, length))
            return False, is_content_incomplete
    # check pub date, check for all content types
    from_time = datetime.datetime.utcnow() - datetime.timedelta(days=_PUBDATE_INTERVAL)
    pub_date = timestamp2datetime(pub_date)
    if pub_date < from_time:
        _LOGGER.warn('[PublishAgent] do not publish %s because too old, pub date: %s' % (info_id, pub_date.strftime('%Y-%m-%d %H:%M:%S')))
        return False, is_content_incomplete
    return True, is_content_incomplete

@perf_logging
def publish_info(locale, info, status, repub=False):
    '''
    Publish info by sending dispatch message
    '''
    res = {'published': False, 'incomplete': False}
    should_publish, res['incomplete'] = _should_publish(info)
    if not should_publish:
        return res
    try:
        _trigger_dispatch(locale, info, status, repub)
        res['published'] = True
    except Exception, err:
        _LOGGER.error('[PublishAgent] trigger dispatch failed with exception: %s, locale: %s' % (err, locale))
    return res

def _trigger_dispatch(locale, info, status, repub):
    '''
    Send dispatch request to dispatch infos to users' inbox.
    '''
    message = {}
    message['infoId'] = info['_id']
    message['infoStatus'] = status
    message['dataType'] = info['type']
    message['locale'] = locale
    message['repub'] = repub
    _handler_repository.process("dispatch_request", message)
    _LOGGER.info('[PublishAgent] send dispatch requset to dispatcher: %s' % info['_id'])
