'''
Created on Nov 19, 2013

@author: fli
'''

import re
from weibonews.utils.format import dict2PropertyTable

_CONN_RE = re.compile(r"(?P<hosts>(?P<host>[A-Z0-9_.-]+)(?P<portpart>:(?P<port>\d+))?(?P<repls>(?P<repl>,[A-Z0-9_.-]+(:\d+)?)*))/(?P<db>\w+)", re.IGNORECASE)

def parse_conn_string(conn_str):
    ''' parse a connection string to a db dict
    '''
    match = _CONN_RE.search(conn_str)
    if match:
        if match.group('repls'):
            host = match.group('hosts')
            port = None
        else:
            host = match.group('host')
            port = int(match.group('port')) if match.group('port') else 27017
        db_address = match.group('db')
        return {
            'server' : host,
            'port' : port,
            'db' : db_address
        }
    else:
        raise ValueError('The connection string "%s" is incorrect.' % conn_str)

def parse_conn_dict(conn_dict):
    result = {}
    for key, conn_str in conn_dict.items():
        result[key] = parse_conn_string(conn_str)
    return result

def cursor_to_array(cursor):
    ''' transform cursor to array
    '''
    items = map(dict2PropertyTable, cursor)
    return items
