'''
Created on: Jun 28, 2013

@author: qwang
'''
import hashlib
import unittest

# configure django settings for test
from django.conf import settings
#NOTICE configure in weibonews/test.py in setUpTests
#settings.configure()

from weibonews.utils.web.decorators import authenticate

class MockRequestFunc(object):
    '''
    Mock object to test decorators
    '''

    def __init__(self):
        self.called = False

    def __call__(self, request, *args):
        self.called = True
        return {'sta': 0}

class TestAuthenticate(unittest.TestCase):

    def setUp(self):
        self.salt = 'dzone test salt'
        self.uid = 2646150270
        self.did = '1234567abcdefg'

    def _mock_settings(self):
        settings.AUTHENTICATION_ENABLED = True
        settings.AUTHENTICATION_FAIL_INFO = 'auth failed'
        settings.COOKIE_PATH = None
        settings.COOKIE_DOMAIN = None
        settings.DOLPHIN_SALT = self.salt
        settings.DEBUG = True

    class mock_weibodb(object):
        '''
        Mock weibodb class to test authenticate
        '''
        token = 'dzone test token'
        def get_weibo_user_token(self, user_id):
            try:
                int(user_id)
            except ValueError:
                return None
            if user_id == 2646150270:
                return self.token
            else:
                # for other uid, return None
                return None

    class mock_request(object):
        def __init__(self, path, method='GET', params=None, user_key=None):
            params = {} if params is None else params
            self.path = path
            self.method = method
            if method == 'GET':
                self.GET = params
            elif method == 'POST':
                self.POST = params
            self.COOKIES = {'user_key': user_key}
            self.raw_post_data = {}

        def build_absolute_uri(self):
            return self.path

    def _gen_user_key(self, weibodb, did=None):
        if did is not None:
            token = did
        else:
            token = weibodb.token
        return hashlib.md5("".join([token, self.salt])).hexdigest()

    def test_authenticate_with_get_request_and_anonymous_user(self):
        '''
        Test auth for anonymous user, with uid, did, user_key all None
        '''
        self._mock_settings()
        func = MockRequestFunc()
        weibodb = TestAuthenticate.mock_weibodb()
        auth_decorator = authenticate(weibodb, settings)
        user_key = None
        request = TestAuthenticate.mock_request('/api/infostream.json', user_key=user_key)
        response = auth_decorator(func)(request)
        self.assertTrue(func.called)
        self.assertTrue(type(response) in [dict, list])

    def test_authenticate_with_get_request_and_key_in_param_with_uid(self):
        '''
        Test auth for get request and auth id in param, auth with uid. did also in param, but because
        uid is provided, will auth with uid. Here the user is already authed, so token will be found
        '''
        self._mock_settings()
        func = MockRequestFunc()
        weibodb = TestAuthenticate.mock_weibodb()
        auth_decorator = authenticate(weibodb, settings)
        user_key = self._gen_user_key(weibodb)
        request = TestAuthenticate.mock_request('/api/infostream.json', params={'uid': self.uid, 'did': self.did}, user_key=user_key)
        response = auth_decorator(func)(request)
        self.assertTrue(func.called)
        self.assertTrue(type(response) in [dict, list])

    def test_authenticate_with_get_request_and_key_in_param_with_wrong_uid(self):
        '''
        Test auth for get request and auth id in param, auth with uid. did also in param, but because
        uid is provided, will auth with uid. Here the user is not authed, so token will be None, will
        auth failed
        '''
        self._mock_settings()
        func = MockRequestFunc()
        weibodb = TestAuthenticate.mock_weibodb()
        auth_decorator = authenticate(weibodb, settings)
        user_key = self._gen_user_key(weibodb)
        request = TestAuthenticate.mock_request('/api/infostream.json', params={'uid': 123456, 'did': self.did}, user_key=user_key)
        auth_decorator(func)(request)
        self.assertTrue(not func.called)

    def test_authenticate_with_get_request_and_key_in_param_with_did(self):
        '''
        Test auth for get request, and auth id in param, auth with did. Here no uid because the user
        is not authed, just auth with did
        '''
        self._mock_settings()
        func = MockRequestFunc()
        weibodb = TestAuthenticate.mock_weibodb()
        auth_decorator = authenticate(weibodb, settings)
        user_key = self._gen_user_key(weibodb, did=self.did)
        request = TestAuthenticate.mock_request('/api/infostream.json', params={'did': self.did}, user_key=user_key)
        response = auth_decorator(func)(request)
        self.assertTrue(func.called)
        self.assertTrue(type(response) in [dict, list])

    def test_authenticate_with_get_request_and_key_in_param_fail(self):
        '''
        Test auth for get request, auth id in request params, with wrong user_key, will auth fail
        '''
        self._mock_settings()
        func = MockRequestFunc()
        weibodb = TestAuthenticate.mock_weibodb()
        auth_decorator = authenticate(weibodb, settings)
        user_key = self._gen_user_key(weibodb) + 'aa'
        request = TestAuthenticate.mock_request('/api/infostream.json', params={'uid': self.uid, 'did': self.did}, user_key=user_key)
        auth_decorator(func)(request)
        self.assertTrue(not func.called)

    def test_authenticate_with_get_request_and_key_in_path_with_uid(self):
        '''
        Test auth for get request, user id in request uri, auth with user id
        '''
        self._mock_settings()
        func = MockRequestFunc()
        weibodb = TestAuthenticate.mock_weibodb()
        auth_decorator = authenticate(weibodb, settings, key_pos=1)
        user_key = self._gen_user_key(weibodb)
        request = TestAuthenticate.mock_request('/api/weibolist/%d.json' % self.uid, user_key=user_key)
        response = auth_decorator(func)(request, self.uid)
        self.assertTrue(func.called)
        self.assertTrue(type(response) in [dict, list])

    # Do not test did in path, we don't use that kind of api any more.
    #def test_authenticate_with_get_request_and_key_in_path_with_did(self):
    #    '''
    #    Test auth for get request, device id in request uri, auth with device id
    #    '''
    #    self._mock_settings()
    #    func = MockRequestFunc()
    #    weibodb = TestAuthenticate.mock_weibodb()
    #    auth_decorator = authenticate(weibodb, settings, key_pos=1)
    #    user_key = self._gen_user_key(weibodb, did=self.did)
    #    request = TestAuthenticate.mock_request('/api/weibolist/%s.json' % self.did, user_key=user_key)
    #    response = auth_decorator(func)(request, self.did)
    #    self.assertTrue(func.called)
    #    self.assertTrue(type(response) in [dict, list])

    def test_authenticate_with_post_request_and_key_in_param_with_uid(self):
        '''
        Test auth for post request, auth id in post body, auth with uid. Here the uid already authed, token will be found
        '''
        self._mock_settings()
        func = MockRequestFunc()
        weibodb = TestAuthenticate.mock_weibodb()
        auth_decorator = authenticate(weibodb, settings, method='POST')
        user_key = self._gen_user_key(weibodb)
        request = TestAuthenticate.mock_request('/api/weibo/pub', method='POST', user_key=user_key, params={'uid': self.uid, 'did': self.did})
        response = auth_decorator(func)(request)
        self.assertTrue(func.called)
        self.assertTrue(type(response) in [dict, list])

    def test_authenticate_with_post_request_and_key_in_param_with_wrong_uid(self):
        '''
        Test auth for post request, auth id in post body, auth with wrong uid. Here uid is not authed, will found None token, auth will failed
        '''
        self._mock_settings()
        func = MockRequestFunc()
        weibodb = TestAuthenticate.mock_weibodb()
        auth_decorator = authenticate(weibodb, settings, method='POST')
        user_key = self._gen_user_key(weibodb)
        request = TestAuthenticate.mock_request('/api/weibo/pub', method='POST', user_key=user_key, params={'uid': 123456, 'did': self.did})
        auth_decorator(func)(request)
        self.assertTrue(not func.called)

    def test_authenticate_with_post_request_and_key_in_param_with_did(self):
        '''
        Test auth for post request, auth id in post body, auth with device id
        '''
        self._mock_settings()
        func = MockRequestFunc()
        weibodb = TestAuthenticate.mock_weibodb()
        auth_decorator = authenticate(weibodb, settings, method='POST')
        user_key = self._gen_user_key(weibodb, did=self.did)
        request = TestAuthenticate.mock_request('/api/weibo/pub', method='POST', user_key=user_key, params={'did': self.did})
        response = auth_decorator(func)(request)
        self.assertTrue(func.called)
        self.assertTrue(type(response) in [dict, list])

if __name__ == '__main__':
    unittest.main()
