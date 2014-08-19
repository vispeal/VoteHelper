#!encoding=utf-8
'''
Created on: Mar 05, 2014

@author: qwang
'''
import sys
sys.path.append('../../')

import unittest

from weibonews.utils.entity import mark_entity, is_in_title

class EntityTest(unittest.TestCase):

    def test_mark_entity_not_exist(self):
        # test basic mark
        content = u'陈凯歌新片《道士下山》已于2月4日在河北香河正式开机。当天，导演陈凯歌、制片人陈红携主演出席了开机仪式。仪式上，陈凯歌说。'
        entity = u"张艺谋"
        expected_result = u'陈凯歌新片《道士下山》已于2月4日在河北香河正式开机。当天，导演陈凯歌、制片人陈红携主演出席了开机仪式。仪式上，陈凯歌说。'
        result = mark_entity(content, entity, 0)
        self.assertEqual(result, expected_result)

    def test_mark_entity(self):
        # test basic mark
        content = u'陈凯歌新片《道士下山》已于2月4日在河北香河正式开机。当天，导演陈凯歌、制片人陈红携主演出席了开机仪式。仪式上，陈凯歌说。'
        entity = u"陈凯歌"
        expected_result = u'<a data-entity="陈凯歌">陈凯歌</a>新片《道士下山》已于2月4日在河北香河正式开机。当天，导演陈凯歌、制片人陈红携主演出席了开机仪式。仪式上，<a data-entity="陈凯歌">陈凯歌</a>说。'
        result = mark_entity(content, entity, 0)
        self.assertEqual(result, expected_result)

        # test single appearance
        content = u'陈凯歌新片《道士下山》已于2月4日在河北香河正式开机。'
        entity = u"陈凯歌"
        expected_result = u'<a data-entity="陈凯歌">陈凯歌</a>新片《道士下山》已于2月4日在河北香河正式开机。'
        result = mark_entity(content, entity, 0)
        self.assertEqual(result, expected_result)

    def test_mark_entity_publication(self):
        # test publication entity with single appearance
        content = u'陈凯歌新片《道士下山》已于2月4日在河北香河正式开机。当天，导演陈凯歌、制片人陈红携主演出席了开机仪式。仪式上，陈凯歌说。'
        entity = u"道士下山"
        expected_result = u'陈凯歌新片<a data-entity="道士下山">《道士下山》</a>已于2月4日在河北香河正式开机。当天，导演陈凯歌、制片人陈红携主演出席了开机仪式。仪式上，陈凯歌说。'
        result = mark_entity(content, entity, 8)
        self.assertEqual(result, expected_result)

        # test publication entity with multiple appearance
        content = u'陈凯歌新片《道士下山》已于2月4日在河北香河正式开机《道士下山》。当天，导演陈凯歌、制片人陈红携主演出席了《道士下山》开机仪式。仪式上，陈凯歌说。'
        entity = u"道士下山"
        expected_result = u'陈凯歌新片<a data-entity="道士下山">《道士下山》</a>已于2月4日在河北香河正式开机《道士下山》。当天，导演陈凯歌、制片人陈红携主演出席了<a data-entity="道士下山">《道士下山》</a>开机仪式。仪式上，陈凯歌说。'
        result = mark_entity(content, entity, 8)
        self.assertEqual(result, expected_result)

        # test appearance without symbol
        content = u'陈凯歌新片道士下山已于2月4日在河北香河正式开机。当天，导演陈凯歌、制片人陈红携主演出席了开机仪式。仪式上，陈凯歌说。'
        entity = u"道士下山"
        expected_result = u'陈凯歌新片道士下山已于2月4日在河北香河正式开机。当天，导演陈凯歌、制片人陈红携主演出席了开机仪式。仪式上，陈凯歌说。'
        result = mark_entity(content, entity, 8)
        self.assertEqual(result, expected_result)

        # test multiple appearance without symbol
        content = u'陈凯歌新片道士下山已于2月4日在河北香河正式开机道士下山。当天，导演陈凯歌、制片人陈红携主演出席了道士下山开机仪式。仪式上，陈凯歌说。'
        entity = u"道士下山"
        expected_result = u'陈凯歌新片道士下山已于2月4日在河北香河正式开机道士下山。当天，导演陈凯歌、制片人陈红携主演出席了道士下山开机仪式。仪式上，陈凯歌说。'
        result = mark_entity(content, entity, 8)
        self.assertEqual(result, expected_result)

    def test_mark_entity_publication_other_symbol(self):
        content = u'陈凯歌新片【道士下山】已于2月4日在河北香河正式开机。当天，导演陈凯歌、制片人陈红携主演出席了开机仪式。仪式上，陈凯歌说。'
        entity = u"道士下山"
        expected_result = u'陈凯歌新片<a data-entity="道士下山">【道士下山】</a>已于2月4日在河北香河正式开机。当天，导演陈凯歌、制片人陈红携主演出席了开机仪式。仪式上，陈凯歌说。'
        result = mark_entity(content, entity, 8)
        self.assertEqual(result, expected_result)

    def test_mark_entity_lower_case(self):
        # single appearance
        content = u'3月5日，上星期五黄晓明以价值二百三十万港币的跑车作生日礼物送给Angelababy，但有传黄晓明买下的原来是张智霖的旧车，让港媒不禁评价黄晓明是个会过日子的人。'
        entity = u'angelababy'
        expected_result = u'3月5日，上星期五黄晓明以价值二百三十万港币的跑车作生日礼物送给<a data-entity="angelababy">Angelababy</a>，但有传黄晓明买下的原来是张智霖的旧车，让港媒不禁评价黄晓明是个会过日子的人。'
        result = mark_entity(content, entity, 9)
        self.assertEqual(result, expected_result)

        # multiple appearance
        content = u'3月5日，上星期五黄晓明以价值二百三十万港币的跑车作生日礼物送给Angelababy，但有传黄晓明买下的原来是Angelababy的旧车，让港媒不禁评价Angelababy是个会过日子的人。'
        entity = u'angelababy'
        expected_result = u'3月5日，上星期五黄晓明以价值二百三十万港币的跑车作生日礼物送给<a data-entity="angelababy">Angelababy</a>，但有传黄晓明买下的原来是Angelababy的旧车，让港媒不禁评价<a data-entity="angelababy">Angelababy</a>是个会过日子的人。'
        result = mark_entity(content, entity, 9)
        self.assertEqual(result, expected_result)

    def test_mark_entity_mix_case(self):
        # multiple appearance
        content = u'3月5日，上星期五黄晓明以价值二百三十万港币的跑车作生日礼物送给AngelaBaby，但有传黄晓明买下的原来是angelababy的旧车，让港媒不禁评价angelababy是个会过日子的人。'
        entity = u'angelababy'
        expected_result = u'3月5日，上星期五黄晓明以价值二百三十万港币的跑车作生日礼物送给<a data-entity="angelababy">AngelaBaby</a>，但有传黄晓明买下的原来是angelababy的旧车，让港媒不禁评价<a data-entity="angelababy">angelababy</a>是个会过日子的人。'
        result = mark_entity(content, entity, 9)
        self.assertEqual(result, expected_result)

    def test_mark_entity_lower_case_publication(self):
        # single appearance
        content = u'3月5日，上星期五黄晓明以价值二百三十万港币的跑车作生日礼物送给《Angelababy》，但有传黄晓明买下的原来是张智霖的旧车，让港媒不禁评价黄晓明是个会过日子的人。'
        entity = u'angelababy'
        expected_result = u'3月5日，上星期五黄晓明以价值二百三十万港币的跑车作生日礼物送给<a data-entity="angelababy">《Angelababy》</a>，但有传黄晓明买下的原来是张智霖的旧车，让港媒不禁评价黄晓明是个会过日子的人。'
        result = mark_entity(content, entity, 8)
        self.assertEqual(result, expected_result)

        # multiple appearance
        content = u'3月5日，上星期五黄晓明以价值二百三十万港币的跑车作生日礼物送给《Angelababy》，但有传黄晓明买下的原来是《Angelababy》的旧车，让港媒不禁评价《Angelababy》是个会过日子的人。'
        entity = u'angelababy'
        expected_result = u'3月5日，上星期五黄晓明以价值二百三十万港币的跑车作生日礼物送给<a data-entity="angelababy">《Angelababy》</a>，但有传黄晓明买下的原来是《Angelababy》的旧车，让港媒不禁评价<a data-entity="angelababy">《Angelababy》</a>是个会过日子的人。'
        result = mark_entity(content, entity, 8)
        self.assertEqual(result, expected_result)

        # multiple appearance
        content = u'3月5日，上星期五黄晓明以价值二百三十万港币的跑车作生日礼物送给《Angelababy》，但有传黄晓明买下的原来是《Angelababy》的旧车，让港媒不禁评价Angelababy是个会过日子的人。'
        entity = u'angelababy'
        expected_result = u'3月5日，上星期五黄晓明以价值二百三十万港币的跑车作生日礼物送给<a data-entity="angelababy">《Angelababy》</a>，但有传黄晓明买下的原来是<a data-entity="angelababy">《Angelababy》</a>的旧车，让港媒不禁评价Angelababy是个会过日子的人。'
        result = mark_entity(content, entity, 8)
        self.assertEqual(result, expected_result)

    def test_is_in_title_basic(self):
        title = u'政协委员张国立:我们拍《纸牌屋》肯定通不过审查'
        entity = u'张国立'
        entity_type = 0
        result = is_in_title(entity, entity_type, title)
        self.assertTrue(result)

        entity = u'冯小刚'
        entity_type = 0
        result = is_in_title(entity, entity_type, title)
        self.assertFalse(result)

    def test_is_in_entity_for_publication(self):
        title = '政协委员张国立:我们拍《纸牌屋》肯定通不过审查'
        entity = '张国立'
        entity_type = 8
        result = is_in_title(entity, entity_type, title)
        self.assertFalse(result)

        entity = '纸牌屋'
        result = is_in_title(entity, entity_type, title)
        self.assertTrue(result)

        title = '政协委员张国立:我们拍【纸牌屋】肯定通不过审查'
        result = is_in_title(entity, entity_type, title)
        self.assertTrue(result)

        title = '政协委员张国立:我们拍“纸牌屋”肯定通不过审查'
        result = is_in_title(entity, entity_type, title)
        self.assertTrue(result)

    def test_is_in_entity_for_publication_unicode(self):
        title = u'政协委员张国立:我们拍《纸牌屋》肯定通不过审查'
        entity = u'张国立'
        entity_type = 8
        result = is_in_title(entity, entity_type, title)
        self.assertFalse(result)

        entity = u'纸牌屋'
        result = is_in_title(entity, entity_type, title)
        self.assertTrue(result)

    def test_is_in_title_with_lower_case(self):
        title = 'AC米兰否认即将购买曼联队长'
        entity = 'ac米兰'
        entity_type = 0
        result = is_in_title(entity, entity_type, title)
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main(verbosity=2)
