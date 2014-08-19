'''
Created on: Aug 12, 2013

@author: qwang
'''
import os
import sys
import unittest

_current_path = os.path.dirname(os.path.realpath(__file__))

def setUpTests():
    # configure django settings for test
    from django.conf import settings
    settings.configure()
    sys.path.insert(0, _current_path)
    from weibonews.db import config, metadb
    # config metadb
    meta_db = {'zh-cn':
        {
            'server': '121.52.224.179',
            'port': 37021,
            'db': 'weibometa_test',
            'cache': None,
        }
    }
    config(metadb, meta_db)

def tearDownTests():
    # drop test databases
    try:
        from weibonews.db import metadb
        metadb.DB.connection.drop_database('weibometa_test')
    except:
        pass

if __name__ == '__main__':
    setUpTests()
    # get current dir path
    current_path = os.path.dirname(os.path.realpath(__file__))
    # auto discover test cases and run them.
    # NOTICE here exclude rabbitmq_blocking_client_test
    tests = unittest.TestLoader().discover(_current_path, pattern='*?[!t]_test.py')
    unittest.TextTestRunner(verbosity=2).run(tests)
    tearDownTests()
