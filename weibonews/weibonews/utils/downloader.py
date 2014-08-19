'''
Created on Dec 14, 2012

@author: fli
'''
import re
import os
import urllib2
import urllib3
import logging
from urlparse import urlparse
from datetime import datetime
from weibonews.utils.decorators import perf_logging
from weibonews.utils.format import valid_link

_LOGGER = logging.getLogger("weibonews.downloader")
USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.56 Safari/537.17"

_REDIRECT_STATUSES = [301, 302, 303, 307, 308]

_NUM_POOLS = 10
_TIMEOUT = 30

_CONTENT_LENGTH_LIMIT = 5000000

_HTTP = urllib3.PoolManager(num_pools = _NUM_POOLS, timeout = _TIMEOUT)

def _valid_content(resp):
    content_type = resp.headers.get('content-type', '')
    if not content_type.startswith('text'):
        return False
    if int(resp.headers.get('content-length', 0)) > _CONTENT_LENGTH_LIMIT:
        return False
    return True

@perf_logging
def head(url):
    '''
    Send HEAD request and return response
    '''
    poll = _HTTP
    try:
        resp = poll.urlopen(method='HEAD', url=url, headers={'User-Agent': USER_AGENT})
        if resp is None:
            _LOGGER.warning("Empty response for head request, url: %s" % url)
        return resp
    except urllib2.HTTPError, err:
        _LOGGER.warning("Http request failed url=%s, Exception: %s" % (url, err))
        return None
    except Exception, err:
        _LOGGER.warning("Request head failed url=%s, Exception: %s" % (url, err))
        return None

@perf_logging
def download(url, follow_redirect=True, need_validate=True, dynamic=False, referer=None, max_try_count=1):
    try_count = 1
    while try_count <= max_try_count:
        resp = _download(url, follow_redirect, need_validate, dynamic, referer)
        if resp is not None:
            break
        try_count += 1
    return resp

@perf_logging
def _download(url, follow_redirect=True, need_validate=True, dynamic=False, referer=None):
    if isinstance(url, unicode):
        url = url.encode('utf8', 'ignore')
    if not isinstance(url, str):
        _LOGGER.error("download url is not str, %s" % url)
        return None

    if need_validate and not valid_link(url):
        _LOGGER.error('download url not valid: %s' % url)
        return None

    pool = _HTTP
    # filter url with ext. if not ext in url, send head request and get
    # content type and content length
    if need_validate:
        need_validate = False
        u = urlparse(url)
        filename = u.path.split('/')[-1]
        if filename.find('.') == -1:
            need_validate = True
    if need_validate:
        # send head request, and valid url by content type and content
        # length
        try:
            resp = pool.urlopen(method="HEAD", url=url, redirect=follow_redirect, headers = {"User-Agent" : USER_AGENT})
            if resp is None:
                _LOGGER.warning("Empty response for head request, url: %s" % url)
                return None
            if not _valid_content(resp):
                _LOGGER.debug('Not valid content, type: %s, length: %d' % (resp.headers.get('Content-Type', ''), resp.headers.get('Content-Length', -1)))
                return None
        except urllib2.HTTPError, err:
            _LOGGER.warning("Http request failed url=%s, Exception: %s" % (url, err))
            return None
        except Exception, err:
            _LOGGER.warning("Request head failed url=%s, Exception: %s" % (url, err))
            return None
    # if dynamic, download dynamic page
    if dynamic:
        return _download_dynamic(url, referer=referer)
    _LOGGER.debug("Start download %s at %s" % (url, datetime.now()))
    try:
        u = urlparse(url)
        if referer is None:
            referer = u.scheme + '://' + u.netloc
        if not follow_redirect:
            resp = pool.urlopen(method = "GET", url = url, redirect=False, headers = {"User-Agent" : USER_AGENT, "Referer": referer}) #Note: need user agent here?
            if resp is None:
                return None
            resp = _process_response(resp, url)
        else:
            while True:
                resp = pool.urlopen(method = "GET", url = url, redirect=False, headers = {"User-Agent" : USER_AGENT, "Referer": referer}) #Note: need user agent here?
                if resp is None:
                    return None
                resp = _process_response(resp, url)
                if resp.status in _REDIRECT_STATUSES:
                    url = resp.original_url
                    if url.startswith('/'):
                        url = u.scheme + "://" + u.netloc + url
                else:
                    break
    except urllib2.HTTPError, err:
        _LOGGER.warning("Download http request failed url=%s, Exception: %s" % (url, err))
        return None
    except Exception, err:
        _LOGGER.warning("Download failed url=%s, Exception: %s" % (url, err))
        return None
    else:
        _LOGGER.debug("Download finished url:%s status:%d at %s." % (url, resp.status, datetime.now()))
    return resp

_ERROR_HEADER = '###RequestError###'
_DYNAMIC_SCRIPT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'download.js')

@perf_logging
def _download_dynamic(url, referer=None):
    '''
    Download dynamic web page with phantomjs. Basicly just do following things:
    1. download webpage, and css, javascript files.
    2. run javascript in original webpage to get real content.
    '''
    u = urlparse(url)
    if referer is None:
        referer = u.scheme + "://" + u.netloc
    try:
        f = os.popen('phantomjs %s %s --user-agent="%s" --referer=%s --timeout=%s' % (_DYNAMIC_SCRIPT_FILE, url, USER_AGENT, referer, _TIMEOUT * 1000))
        body = f.read()
        if body.startswith(_ERROR_HEADER):
            _LOGGER.error('Download by phantom failed, url: %s, error: %s' % (url, body))
            return Response(status=500)
        return Response(body=body)
    except OSError, err:
        _LOGGER.error(err)
    except Exception, err:
        _LOGGER.error('Download by phantom failed url=%s, Exception: %s' % (url, err))
        return None

_META_REFRESH_RE = re.compile(r'<meta (.*?)(http\-equiv\=\"refresh\") (.*?)content\=(.*?)url\=(?P<url>.*?)["\' ]', re.I)

@perf_logging
def _process_response(resp, url):
    # handle meta refresh problem
    if resp.data is not None and len(resp.data) < 1024:
        m = re.search(_META_REFRESH_RE, resp.data)
        if m is not None:
            original_url = m.group('url')
            return Response(status=302, headers=resp.headers, body=resp.data, url=original_url)
    return Response(status = resp.status, headers = resp.headers, body = resp.data, url=url)

class Response(object):
    def __init__(self, status = 200, body = None, headers = None, url=None):
        self.status = status
        self.body = body
        if headers is None:
            headers = {}
        self.headers = headers
        self.original_url = headers.get('location', None) or url

def download2(url):
    req = urllib2.Request(url)
    res = urllib2.urlopen(req)
    body = res.read()
    return Response(res.getcode(), body, res.headers)

def main():
    '''
    main function to test downloader
    '''

    import sys

    url = sys.argv[1]
    start_time = datetime.now()
    resp = download(url)
    end_time = datetime.now()
    print 'download with urllib3: '
    print end_time - start_time, len(resp.body) if resp is not None else 0

    start_time = datetime.now()
    resp = download(url, dynamic=True)
    end_time = datetime.now()
    print 'download with phantomjs: '
    print end_time - start_time, len(resp.body) if resp is not None else 0

    start_time = datetime.now()
    resp = download2(url)
    end_time = datetime.now()
    print 'download with urllib2: '
    print end_time - start_time, len(resp.body) if resp is not None else 0

if __name__ == "__main__":
    main()
