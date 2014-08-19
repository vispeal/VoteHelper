import re
import logging
import chardet
import codecs
from weibonews.utils.decorators import perf_logging

_LOGGER = logging.getLogger("weibonews.extractor")

_CONTENT_TYPE_META_REG_ = re.compile(r'<\s*meta[^>]+charset=\"?([^>]+?)[;\'\">]', re.I)

#copied from BeautifulSoup.BeautifulSoup.CHARSET_RE
_CHARSET_RE = re.compile(r"((^|;)\s*charset=)([^;]*)", re.M)

@perf_logging
def _get_encoding_from_header(headers, body):
    content_type = headers['Content-Type']
    if content_type is not None and (isinstance(content_type, str) or isinstance(content_type, unicode)):
        charset = _CHARSET_RE.search(content_type)
    else:
        charset = None
    return charset and charset.group(3) or None

@perf_logging
def _get_encoding_from_meta(headers, body):
    match = _CONTENT_TYPE_META_REG_.search(body)
    if match is not None:
        encoding = match.group(1).strip().lower()
        if len(encoding) == 0:
            return None
        else:
            return encoding
    else:
        return None

@perf_logging
def _get_encoding_by_chardet(headers, body):
    return chardet.detect(body)['encoding']

@perf_logging
def _try_get_encoding(headers, body, try_count):
    attempts = [_get_encoding_from_header, _get_encoding_from_meta,
                _get_encoding_by_chardet,
                lambda headers, body : "gb2312",
                lambda headers, body : "GBK",
                lambda headers, body : "utf-8", lambda headers, body : None]

    encoding = None
    for i in range(try_count, len(attempts)):
        encoding = attempts[i](headers, body)
        if encoding is not None:
            return encoding, i
    return None, len(attempts)

@perf_logging
def _try_decode(url, body, encode):
    html = None
    try:
        decoder = codecs.lookup(encode)
        if encode == 'utf-8':
            html = decoder.decode(body, 'ignore')[0]
        else:
            html = decoder.decode(body)[0]
    except LookupError:
        _LOGGER.debug("try decode failed, encoding: %s, url: %s, look up codec failed" % (encode, url))
    except UnicodeDecodeError:
        _LOGGER.debug("try decode failed, encoding: %s, url: %s, decode failed" % (encode, url))
    return html

@perf_logging
def decode(url, headers, body, encoding=None):
    '''
    decode html to unicode
    '''

    try_count = 0

    while True:
        if encoding is not None:
            try_count = -1
        else:
            encoding, try_count = _try_get_encoding(headers, body, try_count)
            if encoding is None:
                _LOGGER.error("decoding failed for url %s" % url)
                return None, None
        html = _try_decode(url, body, encoding)
        if html is not None:
            _LOGGER.debug('decode url succeeded, url: %s, encoding: %s, try count: %s' % (url, encoding, try_count))
            return html, encoding
        else:
            try_count += 1
            encoding = None

@perf_logging
def decode_string(string, encoding=None):
    if string is None:
        return None
    if isinstance(string, unicode):
        return string

    if not isinstance(string, str):
        raise Exception("just support decode string")

    try:
        if encoding is None:
            encoding = "utf-8"
        return string.decode(encoding)
    except UnicodeDecodeError:
        encoding = chardet.detect(string)['encoding']
        try:
            decoder = codecs.lookup(encoding)
            return decoder.decode(string, 'ignore')[0]
        except (LookupError, UnicodeDecodeError):
            return None

@perf_logging
def encode_string(string, encoding=None):
    '''
    Encoding string by specific encoding format
    '''
    if string is None:
        return None
    if isinstance(string, str):
        return string
    if not isinstance(string, unicode):
        raise Exception("just support encode unicode")

    if encoding is None:
        encoding = "utf-8"

    try:
        return string.encode("utf-8")
    except UnicodeEncodeError:
        encoding = chardet.detect(string)['encoding']
        try:
            encoder = codecs.lookup(encoding)
            return encoder.encode(string, 'ignore')[0]
        except (LookupError, UnicodeEncodeError):
            return None
