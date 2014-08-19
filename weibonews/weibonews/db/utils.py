'''
Created on Dec 12, 2012

@author: fli
'''

import re
from pymongo import ReadPreference
from pymongo import Connection
from pymongo.collection import SON
from pymongo.master_slave_connection import MasterSlaveConnection
from weibonews.utils.format import dict2PropertyTable

NO_ID = {'_id' : 0}
ID_ONLY = {'_id' : 1}

_CONN_RE = re.compile(r"(?P<hosts>(?P<host>[A-Z0-9_.-]+)(?P<portpart>:(?P<port>\d+))?(?P<repls>(?P<repl>,[A-Z0-9_.-]+(:\d+)?)*))/(?P<db>\w+)", re.IGNORECASE)

def parse_conn_string(conn_str):
    m = _CONN_RE.search(conn_str)
    if m:
        if m.group('repls'):
            host = m.group('hosts')
            port = None
        else:
            host = m.group('host')
            port = int(m.group('port')) if m.group('port') else 27017
        db = m.group('db')
        return {
            'server' : host,
            'port' : port,
            'db' : db
        }
    else:
        raise ValueError('The connection string "%s" is incorrect.' % conn_str)

def parse_conn_dict(conn_dict):
    result = {}
    for key, conn_str in conn_dict.items():
        result[key] = parse_conn_string(conn_str)
    return result

_CONNECTIONS = {}

def connect(host, port=None, replset=None):
    '''
    Connect to the database.
    '''
    assert host, 'host of the database server may not be null.'
    port = port or 27017
    key = (host, port, replset)
    conn = None
    if key in _CONNECTIONS:
        conn = _CONNECTIONS[key]
    else:
        if replset:
            conn = _master_slave_connection(host, port, replset)
        else:
            conn = Connection(host, port)
        _CONNECTIONS[key] = conn
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
        cond = {'_id': coll_name}
        id_info = self.db.ids.find_one(cond)
        if  not id_info:
            self.db.ids.insert({'_id': coll_name, 'seq': 1L})

    def next_id(self, coll):
        """get next increment id and increase it """
        if coll not in self.colls:
            self._ensure_next_id(coll)
        cond = {'_id': coll}
        update = {'$inc': {'seq': 1L}}
        son = SON([('findandmodify', 'ids'),('query', cond),('update', update),('new', True)])
        seq = self.db.command(son)
        return seq['value']['seq']

def cursor_to_array(cursor):
    '''
    Convert mongodb cursor to an array
    '''
    items = map(dict2PropertyTable, cursor)
    return items

class ConnectionPool(dict):

    def __getitem__(self, key):
        if key not in self:
            raise Exception('Connection pool error, key not configure: %s' % key)
        else:
            return super(ConnectionPool, self).__getitem__(key)
