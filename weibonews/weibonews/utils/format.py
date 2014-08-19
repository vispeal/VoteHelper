'''
Created on Dec 12, 2012

@author: fli
'''
import re
import copy
import uuid
import simplejson
import time
import datetime
import calendar
import hashlib
import math
from weibonews.utils import jenkinshash
from urlparse import urlparse

class PropertyTable(dict):
    '''
    A property table that allows create/get/set property that is not in the property list by using attribute syntax.
    '''

    @classmethod
    def fromJson(s, encoding=None, cls=None, object_hook=None, parse_float=None,
    parse_int=None, parse_constant=None, object_pairs_hook=None,
    use_decimal=False, **kw):
        '''
        Creates an PropertyTable from a JSON string.
        '''
        if s:
            json_dict = simplejson.loads(s, encoding=encoding, cls=cls, object_hook=object_hook, parse_float=parse_float, parse_int=parse_int, parse_constant=parse_constant, object_pairs_hook=object_pairs_hook, use_decimal=use_decimal, **kw)
            return PropertyTable(json_dict)
        else:
            return PropertyTable()

    def __getattr__(self, name):
        '''
        Delegate self.name to self[name]. If name not in self, None is returned.
        '''
        if name in self:
            return self[name]
        else:
            return self.getdefault(name)

    def getdefault(self, name):
        '''
        Retrieve the default value of a attribute.
        '''
        base = self.__dict__
        if '__defaults__' in base:
            defaults = base['__defaults__']
            if name in defaults:
                return defaults[name]
        return None

    def setdefault(self, name, value):
        '''
        Retrieve the default value of a attribute.
        '''
        base = self.__dict__
        if '__defaults__' in base:
            defaults = base['__defaults__']
        else:
            defaults = {}
            base['__defaults__'] = defaults
        defaults[name] = value

    def __setattr__(self, name, value):
        '''
        Delegate self.name = value to self[name] = value
        '''
        self[name] = value

    def __delattr__(self, name):
        '''
        Delegate the 'remove' action.
        '''
        del self[name]

    def readOnlyCopy(self):
        '''
        Return a read-only copy of this property table.
        '''
        return ReadOnlyPropertyTable(self)

    def tojson(self, skipkeys=False, ensure_ascii=True, check_circular=True,
        allow_nan=True, cls=None, indent=None, separators=None,
        encoding='utf-8', default=None, use_decimal=False, **kw):
        '''
        Convert the property table to a JSON string.
        '''
        return simplejson.dumps(self, skipkeys=skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular, allow_nan=allow_nan, cls=cls, indent=indent, separators=separators, encoding=encoding, default=default, use_decimal=use_decimal, **kw)


class ReadOnlyPropertyTable(PropertyTable):
    '''
    A read-only property table which attributes or properties can not be changed.
    '''

    def mutableCopy(self):
        '''
        Return a mutable copy of this property table.
        '''
        return PropertyTable(self)

    def setdefault(self, name, value):
        pass

    def __setattr__(self, name, value):
        pass

    def __delattr__(self, name):
        pass

    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
        pass

def dict2PropertyTable(d, recursive=True):
    '''
    Converts an dict to PropertyTable.

    If the give paremeter is not a dict, it is returned directly.
    '''
    if d:
        if isinstance(d, dict) and not isinstance(d, PropertyTable):
            d = PropertyTable(d)
        if recursive:
            if isinstance(d, dict):
                for k in d:
                    d[k] = dict2PropertyTable(d[k])
            elif hasattr(d, '__iter__'):
                d = map(dict2PropertyTable, d)
    return d

def strip(s):
    '''strip and return result of a string is is not None. Otherwise return None.
    '''
    if s is not None and isinstance(s, basestring):
        s = s.strip()
    return s

def content_md5(s):
    '''
    Return md5 digest of just characters of the given string.
    '''
    s = strip(s)
    s = re.sub(r'\s', '', s)
    s = re.sub(u'[^a-zA-Z0-9\u4e00-\u9fa5]', '', s)
    return hashdigest(s, algorithm='md5')

def hashdigest(s, algorithm=None):
    '''
    Return hash digest of a given string, using specified algorithm or default hash.
    '''
    if isinstance(s, unicode):
        s = s.encode('utf-8')
    if algorithm:
        l = hashlib.new(algorithm)
        l.update(s)
        digest = l.hexdigest()
    else:
        digest = '%016x' % unsigned(hash(s))

    return digest

def unsigned(val, base=64):
    '''
    Convert a signed integer to unsigned integer of a given base.
    '''
    max_value = 1 << base
    _checkoverflow(val, max_value)
    if val < 0:
        val += max_value
    return val

def _checkoverflow(val, max_value):
    if abs(val) >= max_value:
        raise Exception('Value %d overflowed.' % val)

def datetime2timestamp(dt):
    '''
    Converts a datetime object to UNIX timestamp in milliseconds.
    '''
    if hasattr(dt, 'utctimetuple'):
        t = calendar.timegm(dt.utctimetuple())
        timestamp = int(t) + float(dt.microsecond) / 1000000
        return timestamp * 1000
    return dt

def datetime2microtimestamp(dt):
    '''
    Converts a datetime object to UNIX timestamp in milliseconds.
    '''
    if hasattr(dt, 'utctimetuple'):
        t = calendar.timegm(dt.utctimetuple())
        timestamp = int(t)*1000000 + dt.microsecond
        return timestamp
    return dt

def timestamp2datetime(timestamp):
    '''
    Converts UNIX timestamp in milliseconds to a datetime object.
    '''
    if isinstance(timestamp, (int, long, float)):
        return datetime.datetime.utcfromtimestamp(timestamp / 1000)
    return timestamp

def diff_seconds(first, second):
    '''
    Get time difference between two datetime with seconds
    '''
    delta = second - first
    return delta.days * 86400 + delta.seconds

def timestamp_now():
    '''
    Get timestamp of current time
    '''
    return int(time.time())

def sigmoid_raw(x):
    return 1.0 / (1.0 + math.exp(-1.0 * x))

def sigmoid(x):
    return sigmoid_raw(x) * 2 - 1

def linear_combine(features, weights):
    score = 0.0
    for name, weight in weights.items():
        score += features[name] * weight

    return score

def simple_params(params):
    entries = []
    for param in params:
        if isinstance(param[1], dict) or isinstance(param[1], list):
            entries.append((param[0], type(param[1])))
        elif (isinstance(param[1], basestring) or isinstance(param[1], unicode)) and len(param[1]) > 1024:
            entries.append((param[0], type(param[1])))
        else:
            if isinstance(param[1], str) and len(param[1]) > 0 and ord(max(param[1])) > 127:
                entries.append((param[0], type(param[1])))
            else:
                entries.append(param)
    return entries

_UNLIKELY_URL_EXT = ['gif', 'png', 'jpg', 'jpeg', 'exe', 'apk', 'swf', 'zip', 'tar', 'gz', 'bz2']

def valid_link(link):
    '''
    Check link is valid or not
    '''
    parse_result = urlparse(link)
    ext = parse_result.path.split('.')[-1]
    if ext in _UNLIKELY_URL_EXT:
        return False
    return True

def list2dict(ori_list):
    '''
    Convert a list to a dict
    '''
    result = {}
    for item in ori_list:
        result[item] = True
    return result

def gen_unique_id():
    unique_id = uuid.uuid1().hex
    return jenkinshash.hashlittle('%s' % unique_id)

class OperationMap(dict):
    '''
    Simple operation map
    '''

    def __init__(self, new_list=None, old_list=None):
        '''
        Operation map can be initialized in 3 ways:
        1. without any parameters: build empty operation map
        2. with new list given, and old list not provided: build operation map with one list
        3. with new list and old list provided: build operation map with two lists
        '''
        super(OperationMap, self).__init__({})
        if new_list is None:
            self['add'] = []
            self['remove'] = []
        elif type(new_list) is list and old_list is None:
            self['add'] = copy.deepcopy(new_list)
            self['remove'] = []
        elif type(new_list) is list and type(old_list) is list:
            # build operation map with two lists
            self['add'] = []
            self['remove'] = []
            for item in new_list:
                if item not in old_list:
                    self['add'].append(item)
                else:
                    old_list.remove(item)
            for item in old_list:
                self['remove'].append(item)
        else:
            raise Exception('Params not supported: %s, %s' % (new_list, old_list))
        # define statuses, for combining two operation maps
        self._replace_statuses = ['finished']
        self._merge_statuses = ['ready', 'rebuilding']

    def combine(self, old_map, status='rebuilding'):
        '''
        Combine old operation map with this object, use status to decide to replace or merge
        '''
        if status in self._merge_statuses:
            self._merge(old_map)
        elif status in self._replace_statuses:
            # will replace old operation map, do not need to change self
            return
        else:
            raise Exception('Unknow status for operation map: %s' % status)

    def _merge(self, other_map):
        '''
        Merge self with other operation map
        '''
        if type(other_map) is not dict:
            raise Exception('Other map must be a dict, not %s' % type(other_map))
        old_add_list = other_map.get('add', [])
        old_remove_list = other_map.get('remove', [])
        for item in old_remove_list:
            # 1. if item both in old add and remove list, remove from old add
            # lsit, do not change self.
            # 2. else, if item in self add list, remove it.
            # 3. else, if item not in self remove list, add it into remove list.
            # 4. else, if item in self remove list, do nothing
            if item in old_add_list:
                old_add_list.remove(item)
            elif item in self['add']:
                self['add'].remove(item)
            elif item not in self['remove']:
                self['remove'].append(item)
        for item in old_add_list:
            # 1. if item in self remove list, remove it, and do not change add
            # list.
            # 2. else, if item not in self add list, add it.
            # 3. else, if item in self add list, do nothing.
            # NOTICE do not need to check old remove list here, because already
            # check above
            if item in self['remove']:
                self['remove'].remove(item)
            elif item not in self['add']:
                self['add'].append(item)


_CLEAN_IMG_RE = re.compile(r"<dolphinimagestart--([0-9a-fA-F]){8}-([0-9a-fA-F]){4}-([0-9a-fA-F]){4}-([0-9a-fA-F]){4}-([0-9a-fA-F]){12}--dolphinimageend>", re.IGNORECASE)
_EXTRA_HTML_TAGS_RE = re.compile(r'<(\/)?(a|b).*?>', re.IGNORECASE)

def clean_content(content):
    '''
    Clean extra information in text content:
    1. remove image placeholder
    2. replace <br> with \n
    3. remove other html tags: <b>
    '''
    if not content:
        return content
    # remove image place holder
    content = _CLEAN_IMG_RE.sub('', content)
    content = content.replace('<p>', '\n')
    content = content.replace('</p>', '\n')
    content = _EXTRA_HTML_TAGS_RE.sub('', content)
    return content.strip(' \r\n')
