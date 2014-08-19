#!/encoding=utf-8
'''
Created on: Aug 06, 2013

@author: qwang
'''
import sys
sys.path.insert(0, '../../')
import unittest

from weibonews.utils import dedupagent

class DedupAgentTest(unittest.TestCase):
    '''
    Test class for deup agent.

    NOTICE this test case can be only run once, duplicate status will change
    if run multiple times.
    '''

    def setUp(self):
        # config dedup agent for china test environment
        dedupagent.config('10.2.8.185:8081')

    def tearDown(self):
        pass

    def test_users_dup(self):
        '''
        Test case for users dedup.
        '''
        doc_id = 123456
        user_ids = [123,124,125,126,127,128]
        res = dedupagent.is_users_dup(user_ids, doc_id)
        self.assertTrue(res is not None and type(res) is dict and 'dup_users' in res)
        for user in user_ids:
            self.assertTrue(user not in res['dup_users'])
        new_user_ids = [123,125,129,130,131]
        res = dedupagent.is_users_dup(new_user_ids, doc_id)
        self.assertTrue(res is not None and type(res) is dict and 'dup_users' in res)
        for user in new_user_ids:
            if user in user_ids:
                self.assertTrue(user in res['dup_users'])
            else:
                self.assertTrue(user not in res['dup_users'])

    def test_weibo_for_users_dup(self):
        '''
        Test case for weibo dup for users
        '''
        weibo_text = u'以同城宠物配对切入的宠物社交应用遛遛正式上线，已获得陌陌早期投资者紫辉的天使投资 |创始人张帆认为他们的优势主要有：产品更专注；更强调宠物主的社交；运营能力更强。国内宠物社区市场暂时还没有特别强大的玩家，移动端更是如此，遛遛有机会成为下个萌宠的陌陌么？http://t.cn/zQCUQFx'
        user_ids = [123,124,125,126,127,128]
        res = dedupagent.is_weibo_dup_for_users(weibo_text, user_ids)
        self.assertTrue(res is not None and type(res) is dict and 'dup_users' in res)
        for user in user_ids:
            self.assertTrue(user not in res['dup_users'])
        weibo_text = u'\r\n以同城宠物配对切入的宠物社交应用遛遛正式上线，已获得陌陌早期投资者紫辉的天使投资 |创始人张帆认为他们的优势主要有：产品更专注；更强调宠物主的社交；运营能力更强。国内宠物社区市场暂时还没有特别强大的玩家，移动端更是如此，遛遛有机会成为下个萌宠的陌陌么？http://t.cn/zQCUQFx\r\n'
        new_user_ids = [123,125,129,130,131]
        res = dedupagent.is_weibo_dup_for_users(weibo_text, new_user_ids)
        self.assertTrue(res is not None and type(res) is dict and 'dup_users' in res)
        for user in new_user_ids:
            if user in user_ids:
                self.assertTrue(user in res['dup_users'])
            else:
                self.assertTrue(user not in res['dup_users'])

if __name__ == '__main__':
    unittest.main(verbosity=2)
