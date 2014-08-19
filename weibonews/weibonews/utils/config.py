'''
Created on Dec 11, 2012

@author: fli
'''
from ConfigParser import SafeConfigParser, NoOptionError, NoSectionError


class FreeConfigParser(SafeConfigParser):

    def _get(self, section, conv, option, default):
        return conv(self.get(section, option, default=default))

    def get(self, section, option, raw=False, config_vars=None, default=None):
        try:
            return SafeConfigParser.get(self, section, option, raw, config_vars)
        except (NoSectionError, NoOptionError), err:
            if default is not None:
                return default
            raise err

    def getint(self, section, option, default=None):
        return self._get(section, int, option, default)

    def getfloat(self, section, option, default=None):
        return self._get(section, float, option, default)

    def getboolean(self, section, option, default=None):
        try:
            return SafeConfigParser.getboolean(self, section, option)
        except (NoSectionError, NoOptionError), err:
            if default is not None:
                return default
            raise err

_SPLITER = '::'

def _list2dict(l1, l2):
    '''
    Convert two list into a dict, values in first list as dict keys and
    values in second list as values. If list2 is not a list, fill dict values
    with list2
    '''
    if type(l1) is not list:
        raise Exception('Error in list2dict: first argument must be list, got %s' % l1)
    if type(l2) is not list:
        result = {}
        for item in l1:
            result[item] = l2
        return result
    if len(l1) != len(l2):
        raise Exception('Error in list2dict: two lists must be in same length: %s, %s' % (l1, l2))
    result = {}
    index = 0
    for item in l1:
        result[item] = l2[index]
        index += 1
    return result

_FALSE_SYMBOLS = ['0', 'false', 'off', 'no', 'False']
_TRUE_SYMBOLS = ['1', 'true', 'on', 'yes', 'True']

def _bool(value):
    if value in _TRUE_SYMBOLS:
        return True
    elif value in _FALSE_SYMBOLS:
        return False
    else:
        raise Exception('Unknow boolean value in config: %s' % value)

class MultiLocaleConfigParser(FreeConfigParser):

    def _ensure_locales(self, section):
        if not hasattr(self, 'locales'):
            locales = self.get(section, 'locales')
            self.locales = locales.split(_SPLITER)
            if len(self.locales) == 0:
                raise Exception('Read locales error: locales is empty: %s' % locales)

    def getlocales(self, section):
        self._ensure_locales(section)
        return self.locales

    def _get_multi(self, section, name, default, formatter):
        self._ensure_locales(section)
        values = self.get(section, name, default)
        if values == default or not values:
            return _list2dict(self.locales, default)
        else:
            values = values.split(_SPLITER)
            if formatter is not None:
                values = [formatter(value) for value in values]
            return _list2dict(self.locales, values)

    def getint(self, section, name, default=None, single=False):
        if not single:
            return self._get_multi(section, name, default, int)
        else:
            return self._get(section, int, name, default)

    def getfloat(self, section, name, default=None, single=False):
        if not single:
            return self._get_multi(section, name, default, float)
        else:
            return self._get(section, float, name, default)

    def getboolean(self, section, name, default=None, single=False):
        if not single:
            return self._get_multi(section, name, default, _bool)
        else:
            try:
                return SafeConfigParser.getboolean(self, section, name)
            except (NoSectionError, NoOptionError), err:
                if default is not None:
                    return default
                raise err

    def getm(self, section, name, default=None):
        return self._get_multi(section, name, default, None)
