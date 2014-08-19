'''
Created on Jan 4, 2013

@author: fli
'''

import urllib2
import urllib
import logging
from weibonews.utils.decorators import perf_logging

_LOGGER  = logging.getLogger("weibonews.downloader")

@perf_logging
def upload(url, data, headers=None):
    try:
        encoded_data = urllib.urlencode(data)
        req = urllib2.Request(url, encoded_data, headers or {})
        f = urllib2.urlopen(req)
    except urllib2.HTTPError,e:
        _LOGGER.warn("upload failed for HTTPError, reason: %s" % e)
        return Response(e.code, e.read())
    except Exception as e:
        _LOGGER.warn("upload failed, reason: %s" % e)
        return None
    else:
        return Response(f.code, f.read(), f.headers)

class Response(object):
    def __init__(self, status = 200, body = None, headers = None):
        if headers is None:
            headers = {}
        self.status = status
        self.body = body
        self.headers = headers or {}

    def __repr__(self):
        return 'Status : %s, Body : %s, Headers : %s' % (self.status, self.body, self.headers)
