#!/usr/bin/env python
# coding: utf-8
"""
Created On Jul 2, 2014

@author: jwang
"""
import simplejson
import hashlib
import urllib
import urllib2


class Paginator(object):
    '''
    Custom paginator class.
    '''

    def __init__(self, current, size):
        self.number = current
        self.size = size
        self.previous_page_number = 1
        self.next_page_number = 1
        self.total = 1
        self.object_list = []

    def get_pages(self, total_num):
        '''
        Get visible pages.
        '''
        total = total_num / self.size
        total = total + 1 if total_num % self.size > 0 else total
        self.total = total
        if total <= 9:
            return [p for p in range(1, total+1)]
        start = 1 if self.number < 5 else self.number - 5
        end = total if self.number + 4 > total else self.number + 4
        end = end if end > 9 else 9
        return [p for p in range(start, end+1)]

    def skip(self):
        skip = (self.number - 1) * self.size
        return 0 if skip < 0 else skip

    def set_list(self, l):
        self.object_list = l

    def has_previous(self):
        b = self.number > 1
        if b:
            self.previous_page_number = self.number - 1
        return b

    def has_next(self):
        b = self.number < self.total
        if b:
            self.next_page_number = self.number + 1
        return b


def _checkoverflow(val, max_v):
    if abs(val) >= max_v:
        raise Exception('Value %d overflowed.' % val)


def unsigned(v, base=64):
    '''
    Convert a signed integer to unsigned integer of a given base.
    '''
    max_v = 1 << base
    _checkoverflow(v, max_v)
    if v < 0:
        v += max_v
    return v


def hashdigest(s, algorithm=None, hexlify=True):
    '''
    Return hash digest of a given string, using specified algorithm or default hash.
    '''
    if s is None:
        return None
    if isinstance(s, unicode):
        s = s.encode('utf-8')
    if algorithm:
        l = algorithm() if callable(algorithm) else hashlib.new(algorithm)
        l.update(s)
        digest = l.hexdigest() if hexlify else False
    else:
        h = hash(s)
        digest = '%016x' % unsigned(h) if hexlify else h
    return digest


def md5(s, hexlify=True):
    '''
    Return md5 digest of a given string.
    '''
    return hashdigest(s, algorithm=hashlib.md5, hexlify=hexlify)


def sha1(s, hexlify=True):
    '''
    Return sha1 digest of a given string.
    '''
    return hashdigest(s, algorithm=hashlib.sha1, hexlify=hexlify)


def request_url(method, url, data=None, fmt=None):
    '''
    Request url by GET or POST method and then transform result to json format optionally.
    '''
    if isinstance(data, dict):
        data_str = urllib.urlencode(data)
    else:
        data_str = ''
    if method == 'GET':
        url = url + '?' + data_str
        req = urllib2.Request(url)
    elif method == 'POST':
        req = urllib2.Request(url, data_str)
    else:
        raise ValueError('Method %s is not supported' % method)
    response = urllib2.urlopen(req)
    result = response.read()
    if fmt == 'json':
        result = simplejson.loads(result)
    return result

