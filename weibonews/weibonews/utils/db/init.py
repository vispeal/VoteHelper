'''
Created on Nov 19, 2013

@author: fli
'''
from pymongo import ReadPreference
from pymongo import Connection
from pymongo.collection import SON
from pymongo.master_slave_connection import MasterSlaveConnection

def config(module, server, port=None, db=None, replset=None):
    '''
    Configure a data access module.
    '''
    assert server and db, 'Either "server" or "db" may not be None.'
    conn = connect(server, port=port, replset=replset)
    module.DB = conn[db]
    module.IDS = IncrementalId(module.DB)
    if hasattr(module, 'INDEXES'):
        ensure_indexes(module, module.INDEXES)
    if hasattr(module, 'JS_FUNC'):
        save_js_funcs(module, module.JS_FUNC)

def save_js_funcs(module, func_table):
    '''
    Save javascript functions
    '''
    for name, func_str in func_table.items():
        module.DB.system.js.save({"_id" : name, "value" : func_str})

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

_CONNECTION = {}

def connect(host, port=None, replset=None):
    '''
    Connect to the database.
    '''
    assert host, 'host of the database server may not be null.'
    port = port or 27017
    key = (host, port, replset)
    conn = None
    if key in _CONNECTION:
        conn = _CONNECTION[key]
    else:
        if replset:
            conn = _master_slave_connection(host, port, replset)
        else:
            conn = Connection(host, port)
        _CONNECTION[key] = conn
    return conn

def _master_slave_connection(master, port, slaves):
    '''
    Master slave connection. Read from secondary.
    '''
    m_con = Connection(master, port)
    s_con = []
    for slave in slaves.split(','):
        items = slave.split(':')
        host = items[0]
        port = int(items[1]) or 27017 if len(items) > 1 else 27017
        s_con.append(Connection(host, port))
    con = MasterSlaveConnection(m_con, s_con)
    con.read_prefrence = ReadPreference.SECONDARY
    return con

class IncrementalId(object):
    """implement incremental id for collection in mongodb
    """
    def __init__(self, db):
        self.db = db
        self.colls = {}

    def _ensure_next_id(self, coll_name):
        """ensure next_id item in collection ,if not, next_id method will throw exception rasie by pymongo"""
        cond = {'_id':coll_name}
        id_info = self.db.ids.find_one(cond)
        if  not id_info:
            self.db.ids.insert({'_id':coll_name, 'seq':1L})

    def next_id(self, coll):
        """get next increment id and increase it """
        if coll not in self.colls:
            self._ensure_next_id(coll)
        cond = {'_id':coll}
        update = {'$inc':{'seq':1L}}
        son = SON([('findandmodify', 'ids'), ('query', cond), ('update', update), ('new', True)])
        seq = self.db.command(son)
        return seq['value']['seq']