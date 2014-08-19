import sys
import logging
from time import time
import hashlib

from django.utils import simplejson
from django.http import HttpResponse, HttpRequest, QueryDict
from weibonews.utils.web.errors import internal_server_error, authentication_fail
from weibonews.utils.web.http import parse_charsets, try_encode
from weibonews.utils.web import get_optional_parameter
from weibonews.utils.format import simple_params
from weibonews.utils.obscure import obscure, unobscure

PERF_LOGGER = logging.getLogger('weibonews.perf')
_LOGGER = logging.getLogger('weibonews.external')

def perf_logging(func):
    """
    Record the performance of each method call.

    Also catches unhandled exceptions in method call and response a 500 error.
    """
    def perf_logged(*args, **kwargs):
        argnames = func.func_code.co_varnames[:func.func_code.co_argcount]
        fname = func.func_name
        module_name = func.func_code.co_filename.split("/")[-1].split('.')[0]
        req = args[0]
        if isinstance(req, HttpRequest) :
            entries = simple_params(zip(argnames[1:], args[1:]) + kwargs.items() + req.GET.items())
            msg = '%s %s -> %s.%s(%s)' % (req.method, req.META['PATH_INFO'], module_name, fname, ','.join('%s=%s' % entry for entry in entries))
        else:
            entries = simple_params(zip(argnames, args) + kwargs.items())
            msg = '%s.%s(%s)' % (module_name, fname, ','.join('%s=%s' % entry for entry in entries))
        startTime = time()
        retVal = func(*args, **kwargs)
        endTime = time()
        PERF_LOGGER.debug('%s <- %s ms.' % (msg, 1000 * (endTime - startTime)))
        return retVal
    return perf_logged

def json_response(func):
    '''
    Convert json result to an HttpResponse containing json string
    '''
    def json_responsed(*args, **kwargs):
        req = args[0]
        retval = func(*args, **kwargs)
        if not isinstance(retval, HttpResponse):
            charset = req.META.get('HTTP_ACCEPT_CHARSET', 'utf-8')
            try:
                #ignore request charset since it might request *, which is not valid
                #charsets = parse_charsets(charset)
                charsets = []
                content = simplejson.dumps(retval, ensure_ascii=False, default=unicode)
                content, charset = try_encode(content, charsets, 'utf-8')
                response = HttpResponse(content, content_type='application/json; charset=%s' % charset)
            except ValueError, err:
                _LOGGER.error(err)
                return internal_server_error(req, err, exc_info=sys.exc_info())
            except Exception, err:
                _LOGGER.error('failed to convert encoding: %s' % err, exc_info=1)
                return internal_server_error(req, 'Unexpected error happened.', exc_info=sys.exc_info())
        else:
            response = retval
        return response
    return json_responsed

def string_response(func):
    '''
    Convert string result to an HttpResponse containing
    '''
    def string_responsed(*args, **kwargs):
        req = args[0]
        retval = func(*args, **kwargs)
        if not isinstance(retval, HttpResponse):
            charset = req.META.get('HTTP_ACCEPT_CHARSET', 'utf-8')
            try:
                response = HttpResponse(retval, content_type='text/html; charset=%s' % charset)
            except ValueError, err:
                _LOGGER.error("Error:%s. retval: %s" % (err, retval))
                return internal_server_error(req, err, exc_info=sys.exc_info())
            except Exception, err:
                _LOGGER.error('failed to convert encoding: %s' % err, exc_info=1)
                return internal_server_error(req, 'Unexpected error happened.', exc_info=sys.exc_info())
        else:
            response = retval
        return response
    return string_responsed

def obscure_json_response(func):
    def _obscure_json_response(*args, **kwargs):
        req = args[0]
        https_req, error = get_optional_parameter(req, 'https', default=0, formatter=int)
        if error:
            https_req = 1
        retval = func(*args, **kwargs)
        if not isinstance(retval, HttpResponse):
            charset = req.META.get('HTTP_ACCEPT_CHARSET', 'utf-8')
            try:
                charsets = parse_charsets(charset)
                content = simplejson.dumps(retval, ensure_ascii=False)
                content, charset = try_encode(content, charsets, 'utf-8')
                if https_req < 1:
                    #only obscure response for request without https
                    content = obscure(content)
                response = HttpResponse(content, content_type='application/json; charset=%s' % charset)
            except ValueError, err:
                _LOGGER.error(err)
                return internal_server_error(req, err, exc_info=sys.exc_info())
            except Exception, err:
                _LOGGER.error('failed to convert encoding: %s' % err, exc_info=1)
                return internal_server_error(req, 'Unexpected error happened.', exc_info=sys.exc_info())
        else:
            response = obscure(str(retval))
        return response
    return _obscure_json_response

def unobscure_post_request(func):
    def _unobscure_post_request(*args, **kwargs):
        req = args[0]
        https_req, error = get_optional_parameter(req, 'https', default=0, formatter=int)
        if error:
            https_req = 1
        if https_req < 1:
            #only need to unobscure parameters for request without https
            post_data = unobscure(req.raw_post_data)
            req.POST = QueryDict(post_data)
        return func(*args, **kwargs)
    return _unobscure_post_request

class authenticate(object):
    def __init__(self, db, settings, key_pos = None, method = "GET"):
        self._userdb = db
        self._key_pos = key_pos
        # just support auth with uid and did
        self._key_names = ['uid', 'did']
        self._key_formatters = [int, str]
        self._method = method
        self._enabled = settings.AUTHENTICATION_ENABLED
        self._fail_info = settings.AUTHENTICATION_FAIL_INFO
        self._cookie_path = settings.COOKIE_PATH
        self._cookie_domain = settings.COOKIE_DOMAIN
        self._dolphin_salt = settings.DOLPHIN_SALT

    def __call__(self, func):
        def authenticate_func(*args, **kwargs):
            if not self._enabled:
                return func(*args, **kwargs)

            req = args[0]
            user_key = req.COOKIES.get("user_key", None)
            auth_id = None
            key_name = None
            if self._key_pos is not None:
                try:
                    auth_id = args[self._key_pos]
                except IndexError as err:
                    return internal_server_error(req, err, sys.exc_info())
            else:
                for i in range(len(self._key_names)):
                    # default formatter is str
                    key_name = self._key_names[i]
                    fmt = self._key_formatters[i] if i < len(self._key_formatters) else str
                    auth_id, error = get_optional_parameter(req, key_name, formatter=fmt, default=None, method=self._method)
                    if error:
                        return error
                    elif auth_id is not None:
                        break

            success = self._authenticate(key_name, auth_id, user_key)
            if success:
                retval = func(*args, **kwargs)
                if isinstance(retval, HttpResponse) and user_key is not None:
                    retval.set_cookie("user_key", user_key, path=self._cookie_path, domain=self._cookie_domain, httponly=True)
                    return retval
                else:
                    return retval
            else:
                return authentication_fail(req, self._fail_info)

        return authenticate_func

    def _authenticate(self, key_name, auth_id, user_key):
        if auth_id is None and user_key is None:
            #anonymous user
            return True

        if auth_id is None or user_key is None:
            _LOGGER.warn("auth fail, user_id:%s, user_key:%s" % (auth_id, user_key))
            return False

        # if can not get key_name, default is uid
        key_name = key_name or 'uid'
        user_token = None
        # use different auth method for uid and did
        if key_name == 'uid':
            try:
                user_id = int(auth_id)
                user_token = self._userdb.get_weibo_user_token(user_id)
            except ValueError, err:
                _LOGGER.warn("auth fail, get_access_token. error: %s" % err)
                return False
            except Exception, err:
                _LOGGER.error(err)
                return False
        elif key_name == 'did':
            user_token = auth_id
        else:
            _LOGGER.warn('auth failed, not supported key name: %s' % key_name)
            return False

        if user_token is None:
            _LOGGER.warn("auth fail, user_id is %s but user_token is None" % auth_id)
            return False

        expected_user_key = hashlib.md5("".join([user_token, self._dolphin_salt])).hexdigest()
        if expected_user_key != user_key:
            _LOGGER.warn("auth fail, expected:%s, actual:%s" % (expected_user_key, user_key))
        return expected_user_key == user_key
