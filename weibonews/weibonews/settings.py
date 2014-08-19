# -*- encoding: utf-8
'''
Created on: Aug 01, 2013

@author: qwang

Global settings for weibonews
'''

class AuthType(object):
    '''
    User auth type
    '''
    DEVICE = 'device'
    WEIBO = 'weibo'
    # for virtual category user
    CATEGORY = 'category'
    # anonymous user
    ANONYM = 'anonym'

class Priority(object):
    HIGH = 0
    MEDIUM = 1
    LOW = 2

    @classmethod
    def compare(cls, p1, p2):
        '''
        Compare priority. return 1, 0, or -1 as following:
        1. if p1 is higher than p2, return 1.
        2. if p1 is equal with p2, return 0
        3. if p1 is lower than p2, return -1
        '''
        if p1 < p2:
            return 1
        elif p1 == p2:
            return 0
        else:
            return -1

class InfoTag(object):
    NORMAL = 0       # deprecated, use InfoStatus.NORMAL
    ALL = 1

class InfoStatus(object):
    RAW        = -24  #raw weibo which has no news extracted
    OLD        = -19  #old news
    DUPLICATED = -18  #duplicated news
    OBSOLETE   = -17  #not display in article list
    UNPUBLISH  = -16  #unpublished weibo news
    MANUAL     = -10  #editor manually edit
    ADDRECORD  =  -9  #editor add record
    PENDING    =  -8  #weibo news which is waiting for approving to publish
    SENSITIVE  =  -7  #news has sensitive infomation
    INCOMPLETE =  -6  #news has extracting problem
    TRASH      =  -5  #news has no value
    WRONGCLASS =  -4  #news gave inappropriate classification
    OTHERS     =  -3  #news could not be published because of unknown reason
    TABONLY    =  -1  #news been published into tab only, not in recommender
    NORMAL     =   0  #published normal weibo news
    DEEP       =   4  #deep news for keyword recommender
    FEATURED   =   8  #published featured weibo news
    TOP        =  16  #published top news
    BANNER     =  32  #published banner news

class SourceStatus(object):
    ERROR      = -16 # extracting error
    STOPPED    =  -8 # stopped
    RUNNING    =   0 # running

class LinkStatus(object):
    UNKNOW     = -24 # unknow link status
    NOTEXISTS  = -16 # link not exists in system
    FAIL       =  -8 # extract failed
    SUCCESS    =   0 # extract succeed
    FILTERED   =   8 # filtered by newsfilter

TYPE_MAP = {
    'news': 0,
    'placeholder0': 1, # userd by old version clients for other purpose
    'placeholder1': 2, # userd by old version clients for other purpose
    'placeholder2': 3, # userd by old version clients for other purpose
    'placeholder3': 4, # userd by old version clients for other purpose
    'gallery' : 5,
    'video' : 6,
    'post' : 7,
    'index': 8,
    'beauty': 9,
}

class SourceType(object):
    PORTAL = 'portal'
    RSS = 'rss'
    ROLL = 'roll'
    GALLERY = 'gallery'
    FTRSS = 'ftrss'
    APP = 'app'
    BEAUTY = 'beauty'

LOCALE_ID_MAP = {
    "zh-cn": 0,
    "ja-jp": 1,
    "id-id": 2,
    "ar-eg": 3,
    "pt-br": 4,
    "es-mx": 5,
    "th-th": 6,
    "tr-tr": 7,
    "ru-ru": 8,
    "es-ar": 9,
    "zh-hk": 10,
    "zh-tw": 11,
    "ms-my": 12,
    "en-ph": 13,
    "vi-vn": 14,
    "ar-sa": 15,
    "ar-ae": 16,
}

# category priority related defination and actions

CATEGORY_PRIORIYIES = {
    12: 1,
    28: -1,
}
DEFAULT_PRIORITY = 0

def get_category_priority(cat_id):
    '''
    Return priority of category. For now just use 2 level. News category can
    promotion from lower level to higher level.
    '''
    return CATEGORY_PRIORIYIES.get(cat_id, DEFAULT_PRIORITY)

def can_promote_category(cat_id):
    return get_category_priority(cat_id) > -1

