'''
Created on Dec 31, 2011

@author: fli
'''
import logging
import base64
import urllib
import simplejson
from urllib2 import urlopen, URLError, Request
from weibonews.utils.decorators import perf_logging

_LOGGER = logging.getLogger('weibonews.external')

_ACCESS_URL_FORMAT = "http://%s/image/%s/%s"
_INFO_URL_FORMAT = "http://%s/imageinfo/"
_PARAM_ENCODING_FORMAT = "w=%d&q=%d"
_DEFAULT_IMAGE_QUALITY = 80
_SAFE_QUOTE = '/?=&:#%'
_CROP_PARAM_VALUE = "crop=1&rate=16d10&ff=1"

def get_image_access_url(server, url, width=0, quality=_DEFAULT_IMAGE_QUALITY, refer=None, cut=False):
    if url:
        if isinstance(url, unicode):
            url = urllib.quote(url.encode('utf8'), _SAFE_QUOTE)
        if refer is not None:
            url = _encode_refer(url, refer)
        url_encoded = base64.urlsafe_b64encode(url)
        if cut:
            param_encoded = base64.urlsafe_b64encode(_CROP_PARAM_VALUE)
        else:
            param_encoded = base64.urlsafe_b64encode(_PARAM_ENCODING_FORMAT % (width, quality))
        return _ACCESS_URL_FORMAT % (server, url_encoded, param_encoded)
    else:
        return url

@perf_logging
def request_images_size(server, url_list, refer=None):
    if url_list:
        request_urls = []
        for url in url_list:
            if not url:
                continue
            if refer is not None:
                url = _encode_refer(url, refer)
            request_urls.append(url)
        return _get_image_details(server, request_urls)
    return None

@perf_logging
def _encode_refer(url, refer):
    headers = {'Referer': refer}
    url_params = {'headers': urllib.urlencode(headers)}
    return '|'.join((url, urllib.urlencode(url_params)))

@perf_logging
def _get_image_details(server, urls):
    if isinstance(urls, list):
        data = {"u": '[%s]' % ','.join(['"%s"' % u for u in urls])}
        data = urllib.urlencode(data)
        server_url = _INFO_URL_FORMAT % server
        request = Request(server_url, data)
        request.add_header("Content-type", "application/x-www-form-urlencoded")
        try:
            page = urlopen(request).read()
        except URLError, err:
            _LOGGER.error("[Image Compress Service] Error: %s, url %s, data %s" % (err, server_url, data))
            return None
        result = simplejson.loads(page)
        _LOGGER.info("[Image Compress Service] Get %d result from %d request from %s" % (len(result['data']), len(urls), server_url))
        return result['data']
    return None

