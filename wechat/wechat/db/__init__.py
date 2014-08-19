#!/usr/bin/env python
# coding: utf-8
"""
Created On Jul 2, 2014

@author: jwang
"""
from weibonews.db.utils import connect, IncrementalId

def config(module, server, port=None, db=None, replset=None, params=None):
    '''
    Configure a data access module.
    '''
    assert server and db, 'Either "server" or "db" may not be None.'
    params = {} if params is None else params
    conn = connect(server, port=port, replset=replset)
    module.DB = conn[db]
    module.IDS = IncrementalId(module.DB)
    if hasattr(module, 'INDEXES'):
        ensure_indexes(module, module.INDEXES)

def ensure_index(module, collection_name, indexes):
    '''
    Ensure a data access module's collection indexes.
    '''
    collection = module.DB[collection_name]
    for index in indexes:
        collection.ensure_index(index)

def ensure_indexes(module, index_table):
    '''
    Ensure a data access module's indexes.
    '''
    for collection, indexes in index_table.items():
        ensure_index(module, collection, indexes)
