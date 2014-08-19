'''
Created on Jan 8, 2013

@author: fli
'''
import logging
import traceback
import simplejson

from weibonews.utils import jenkinshash
from weibonews.utils.downloader import download
from weibonews.utils.uploader import upload
from weibonews.utils.decorators import perf_logging

_LOGGER = logging.getLogger("weibonews.external")

SERVER_ADDRESS = ''
USER_DUP_API_FORMANT = "http://%s/news/user_dup?uid=%s&did=%s"
USERS_DUP_API_FORMANT = "http://%s/news/users_dup"
GLOBAL_DUP_API_FORMANT = "http://%s/news/global_dup"
GLOBAL_DUP_API = ''
USERS_DUP_API = ''

@perf_logging
def config(server):
    global SERVER_ADDRESS, GLOBAL_DUP_API, USERS_DUP_API
    SERVER_ADDRESS = server
    GLOBAL_DUP_API = GLOBAL_DUP_API_FORMANT % SERVER_ADDRESS
    USERS_DUP_API = USERS_DUP_API_FORMANT % SERVER_ADDRESS

@perf_logging
def is_user_dup(user_id, doc_id):
    if user_id is None or doc_id is None:
        return True
    url = USER_DUP_API_FORMANT % (SERVER_ADDRESS, user_id, doc_id)
    resp = download(url)
    if resp is None or resp.status != 200:
        _LOGGER.error("[Dedup] Unexcepted result from dedup service. (url: %s status %d)" % (url, resp.status if resp else 0))
        return False
    try:
        data = simplejson.loads(resp.body)
        if isinstance(data, dict) and 'dup' in data:
            return data['dup']
    except simplejson.JSONDecodeError, err:
        _LOGGER.error("[Dedup] Failed to load response from dedup service. (url: %s body %s)" % (url, resp.body))
        _LOGGER.error("[Dedup] err: %s traceback %s" % (err, traceback.format_exc()))
        return False
    return False

@perf_logging
def is_users_dup(user_ids, doc_id):
    if user_ids is None or doc_id is None:
        return True
    data = {
        'did': doc_id,
        'uids': user_ids,
    }
    resp = upload(USERS_DUP_API, data)
    if resp is None or resp.status != 200:
        _LOGGER.error("[Dedup] Unexcepted result from dedup service. (url: %s status %d)" % (USERS_DUP_API, resp.status if resp else 0))
        return None
    try:
        data = simplejson.loads(resp.body)
        if isinstance(data, dict):
            return data
    except simplejson.JSONDecodeError, err:
        _LOGGER.error("[Dedup] Failed to load response from dedup service. (url: %s body %s)" % (USERS_DUP_API, resp.body))
        _LOGGER.error("[Dedup] err: %s traceback %s" % (err, traceback.format_exc()))
        return None
    return None

def _text_hash(text):
    '''
    Get hash value of text.
    '''
    return jenkinshash.hashlittle(text.strip())

@perf_logging
def is_weibo_dup_for_users(weibo_text, user_ids):
    '''
    Check if weibo for users duplicated.
    '''
    weibo_text_id = _text_hash(weibo_text)
    return is_users_dup(user_ids, weibo_text_id)

@perf_logging
def is_global_dup(doc_id, title, content, pub_date):
    data = generate_dedup_data(doc_id, title, content, pub_date)
    resp = upload(GLOBAL_DUP_API, data)
    if resp is None or resp.status != 200:
        _LOGGER.error("[Dedup] Unexcepted result from dedup service. (url: %s data %s status %d)" % (GLOBAL_DUP_API, data, resp.status if resp else 0))
        return False
    try:
        data = simplejson.loads(resp.body)
        if isinstance(data, dict) and 'dupId' in data:
            return data['dupId']
    except simplejson.JSONDecodeError, err:
        _LOGGER.error("[Dedup] Failed to load response from dedup service. (url: %s data %s body %s)" % (GLOBAL_DUP_API, data, resp.body))
        _LOGGER.error("[Dedup] err: %s traceback %s" % (err, traceback.format_exc()))
        return False
    return False

@perf_logging
def generate_dedup_data(doc_id, title, content, pub_date):
    if isinstance(title, unicode):
        title = title.encode('utf8')
    if isinstance(content, unicode):
        content = content.encode('utf8')
    data = {'did': doc_id, 'title': title, 'content': content, 'pub': pub_date}
    return data
