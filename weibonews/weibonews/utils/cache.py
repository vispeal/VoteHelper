'''
Created on: May 09, 2013
@author: qwang
Memcache client
'''

import memcache
from weibonews.utils.decorators import perf_logging

_TIMEOUT = 0

class CacheClient:

    def __init__(self, servers, timeout=_TIMEOUT):
        if isinstance(servers, basestring):
            self._client = memcache.Client(servers.split(','))
        else:
            self._client = memcache.Client(servers)
        self._timeout = timeout

    @perf_logging
    def set(self, key, value, timeout=_TIMEOUT):
        if type(key) is not str:
            key = str(hash(str(key)))
        return self._client.set(key, value, time=timeout or self._timeout)

    @perf_logging
    def get(self, key):
        if type(key) is not str:
            key = str(hash(str(key)))
        return self._client.get(key)

    @perf_logging
    def delete(self, key):
        if type(key) is not str:
            key = str(hash(str(key)))
        self._client.delete(key)

    @perf_logging
    def withdraw(self, key):
        if type(key) is not str:
            key = str(hash(str(key)))
        result = self._client.get(key)
        if result:
            self._client.delete(key)
        return result
