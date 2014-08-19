#!encoding=utf-8
'''
Created on: Aug 9, 2013

@author: qwang
'''
import time
import unittest
import sys
sys.path.append('../../')
from weibonews.utils.format import OperationMap, gen_unique_id, clean_content

class OperationMapTest(unittest.TestCase):
    '''
    Test case for operation map
    '''

    def test_init_with_empty(self):
        op_map = OperationMap()
        self.assertTrue('add' in op_map)
        self.assertTrue('remove' in op_map)

    def test_init_with_list(self):
        list_a = [1,2,3]
        op_map = OperationMap(list_a)
        self.assertTrue(op_map['add'] == list_a)
        self.assertTrue(len(op_map['remove']) == 0)

    def test_init_with_lists_1(self):
        list_a = [1,2,3]
        list_b = [3,4,5]
        op_map = OperationMap(list_a, list_b)
        self.assertTrue(len(op_map['add']) == 2)
        self.assertTrue(len(op_map['remove']) == 2)
        self.assertTrue(op_map['add'] == [1,2])
        self.assertTrue(op_map['remove'] == [4,5])

    def test_init_with_lists_2(self):
        list_a = [1,2,3]
        list_b = []
        op_map = OperationMap(list_a, list_b)
        self.assertTrue(len(op_map['add']) == 3)
        self.assertTrue(len(op_map['remove']) == 0)
        self.assertTrue(op_map['add'] == [1,2,3])
        self.assertTrue(op_map['remove'] == [])

    def test_init_with_lists_3(self):
        list_a = []
        list_b = [1,2,3]
        op_map = OperationMap(list_a, list_b)
        self.assertTrue(len(op_map['add']) == 0)
        self.assertTrue(len(op_map['remove']) == 3)
        self.assertTrue(op_map['add'] == [])
        self.assertTrue(op_map['remove'] == [1,2,3])

    def test_combine_merge_with_status_rebuilding(self):
        status = 'rebuilding'
        old_map = {
            'add': [1,2,3],
            'remove': [3,4,5],
        }
        op_map = OperationMap()
        op_map['add'] = [1,3,6,7]
        op_map['remove'] = [4,2]
        op_map.combine(old_map, status)
        self.assertTrue(op_map['add'] == [1,3,6,7])
        self.assertTrue(op_map['remove'] == [4,5])

    def test_combine_merge_with_status_rebuilding_2(self):
        status = 'rebuilding'
        old_map = {
            'add': [1,2],
            'remove': [3,4,5],
        }
        op_map = OperationMap()
        op_map['add'] = [1,3,6,7]
        op_map['remove'] = [4,2]
        op_map.combine(old_map, status)
        self.assertTrue(op_map['add'] == [1,6,7])
        self.assertTrue(op_map['remove'] == [4,5])

    def test_combine_merge_with_status_rebuilding_3(self):
        status = 'rebuilding'
        old_map = {
            'add': [1,2],
            'remove': [3,4,5],
        }
        op_map = OperationMap()
        op_map['add'] = [6,7]
        op_map['remove'] = [9]
        op_map.combine(old_map, status)
        self.assertTrue(op_map['add'] == [6,7,1,2])
        self.assertTrue(op_map['remove'] == [9,3,4,5])

    def test_combine_merge_with_status_ready(self):
        status = 'ready'
        old_map = {
            'add': [1,2],
            'remove': [3,4,5],
        }
        op_map = OperationMap()
        op_map['add'] = [6,7]
        op_map['remove'] = [9]
        op_map.combine(old_map, status)
        self.assertTrue(op_map['add'] == [6,7,1,2])
        self.assertTrue(op_map['remove'] == [9,3,4,5])

    def test_combine_replace(self):
        status = 'finished'
        old_map = {
            'add': [1,2],
            'remove': [3,4,5],
        }
        op_map = OperationMap()
        op_map['add'] = [6,7]
        op_map['remove'] = [9]
        op_map.combine(old_map, status)
        self.assertTrue(op_map['add'] == [6,7])
        self.assertTrue(op_map['remove'] == [9])

class GenerateUniqueIdTest(unittest.TestCase):
    '''
    Test for generate unique id
    '''
    def test_generate(self):
        uid = gen_unique_id()
        self.assertTrue(type(uid) is int)
        self.assertTrue(uid >= 0 and uid <= 4294967295)

    def test_generate_dup_and_perf(self):
        id_map = {}
        start = time.time()
        count = 10
        dup_count = 0
        for _ in range(count):
            uid = gen_unique_id()
            if uid in id_map:
                dup_count += 1
            id_map[uid] = True
            self.assertTrue(uid >= 0 and uid <= 4294967295)
        cost = time.time() - start
        print 'duplicated count: %d, all count: %d' % (dup_count, count)
        print 'generate %d ids cost %f' % (count, cost)
        print 'average generate cost: %f' % (cost / count)

    def test_gen_twice_dup_rate(self):
        id_map = {}
        start = time.time()
        count = 10
        dup_count = 0
        for _ in range(count):
            uid = gen_unique_id()
            self.assertTrue(uid >= 0 and uid <= 4294967295)
            if uid < 1000:
                print uid
            if uid in id_map:
                # generate again
                uid = gen_unique_id()
                self.assertTrue(uid >= 0 and uid <= 4294967295)
                if uid in id_map:
                    dup_count += 1
            id_map[uid] = True
        cost = time.time() - start
        print 'duplicated count: %d, all count: %d' % (dup_count, count)
        print 'generate %d ids cost %f' % (count, cost)
        print 'average generate cost: %f' % (cost / count)

class FormatTest(unittest.TestCase):

    def test_clean_content_basic(self):
        content = u"""<p><b>新浪<a data-src="fake_src">军事</a>编者：</b></p><p>“枭龙”出口所面临的困难</p><dolphinimagestart--1e2be664-9688-3146-8ae4-bb067808bfb1--dolphinimageend><p>（新浪军事）</p>"""
        expected_result = u"""新浪军事编者：\n\n“枭龙”出口所面临的困难\n\n（新浪军事）"""
        result = clean_content(content)
        self.assertEqual(result, expected_result)

    def test_clean_content_contains_unknow_tags(self):
        content = u"""<p><b>新浪<a data-src="fake_src">军事</a><c>编者</c>：</b></p><p>“枭龙”出口所面临的困难</p><dolphinimagestart--1e2be664-9688-3146-8ae4-bb067808bfb1--dolphinimageend><p>（新浪军事）</p>"""
        expected_result = u"""新浪军事<c>编者</c>：\n\n“枭龙”出口所面临的困难\n\n（新浪军事）"""
        result = clean_content(content)
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main(verbosity=2)
