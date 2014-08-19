'''
Created on Mar 19, 2011

@author: chzhong
'''
_TOP_DOMAINS = ['com', 'edu', 'gov', 'int', 'mil', 'net', 'org', 'biz', 'info', 'pro', 'name', 'museum', \
        'coop', 'aero', 'idv', 'xxx']

def parse_charsets(charset_string):
    '''
    Parse charsets from string
    '''
    index = charset_string.find(';')
    if index > 0:
        charset_string = charset_string[:index]
    charsets = charset_string.split(',')
    return [c.strip() for c in charsets]

def try_encode(text, charsets, default='utf-8'):
    '''
    Encoding text by specified charsets
    '''
    if not text or not isinstance(text, unicode):
        return text
    result = None
    result_charset = None
    for charset in charsets:
        try:
            result = text.encode(charset)
            result_charset = charset
            break
        except UnicodeEncodeError:
            pass
    if not result:
        if default:
            result = text.encode(default)
            result_charset = default
        else:
            raise ValueError('"%s" cannot be encoding in any charset of %s.' % (text, charsets))
    return result, result_charset
