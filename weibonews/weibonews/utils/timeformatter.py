#!encoding=utf-8
'''
Created on Dec 14, 2011

@author: qwang

Parse a time string to datetime object.

1. Retreive timezone information from time string, get the tzinfo object, or generate one.
2. Get datetime object with the other information except timezone.
3. Apply the timezone to datetime, and convert to UTC time.
'''
import re
from pytz import utc, timezone, exceptions
from pytz.reference import FixedOffset as Offset
from datetime import datetime, timedelta
from weibonews.utils.format import timestamp2datetime

_formatters = [
        '%a, %d %b %Y %H:%M:%S %Z',
        '%a, %d %B %Y %H:%M:%S %Z',
        '%a, %d %b %Y %H:%M %Z',
        '%a, %d %B %Y %H:%M %Z',
        '%Y/%m/%d %H:%M:%S',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y年%m月%d日 %H:%M:%S',
        '%Y年%m月%d日 %H:%M',
        '%Y年%m月%d日\xa0%H:%M',
        '%Y年%m月%d日%H:%M',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%dT%H:%M:%S%Z',
        '%m-%d %H:%M',
        '(%m/%d %H:%M)',
        '%m/%d %H:%M',
        '%H:%M',
    ]

_time_res = [
        # all fields
        ur'(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+) (?P<hour>\d+):(?P<minute>\d+):(?P<second>\d+)',
        ur'(?P<year>\d+)\-(?P<month>\d+)\-(?P<day>\d+) (?P<hour>\d+):(?P<minute>\d+):(?P<second>\d+)',
        ur'(?P<year>\d+)\u5E74(?P<month>\d+)\u6708(?P<day>\d+)\u65E5 (?P<hour>\d+):(?P<minute>\d+):(?P<second>\d+)',
        # no second
        ur'(?P<year>\d+)\-(?P<month>\d+)\-(?P<day>\d+) (?P<hour>\d+):(?P<minute>\d+)',
        ur'(?P<year>\d+)\.(?P<month>\d+)\.(?P<day>\d+) (?P<hour>\d+):(?P<minute>\d+)',
        ur'(?P<year>\d+)\-(?P<month>\d+)\-(?P<day>\d+)T(?P<hour>\d+):(?P<minute>\d+)',
        ur'(?P<year>\d+)\-(?P<month>\d+)\-(?P<day>\d+), (?P<hour>\d+):(?P<minute>\d+)',
        ur'(?P<year>\d+)\-(?P<month>\d+)\-(?P<day>\d+)\xa0\xa0(?P<hour>\d+):(?P<minute>\d+)',
        ur'(?P<year>\d+)\u5E74(?P<month>\d+)\u6708(?P<day>\d+)\u65E5 (?P<hour>\d+):(?P<minute>\d+)',
        ur'(?P<year>\d+)\u5E74(?P<month>\d+)\u6708(?P<day>\d+)\u65E5\xa0(?P<hour>\d+):(?P<minute>\d+)',
        ur'(?P<year>\d+)\u5E74(?P<month>\d+)\u6708(?P<day>\d+)\u65E5(?P<hour>\d+):(?P<minute>\d+)',
        # no year, second
        ur'(?P<month>\d+)\u6708(?P<day>\d+)\u65E5 (?P<hour>\d+):(?P<minute>\d+)',
        # no time
        ur'(?P<year>\d+)\u5E74(?P<month>\d+)\u6708(?P<day>\d+)\u65E5',
        ur'(?P<year>\d+)-(?P<month>\d+)-(?P<day>\d+)',
]

_timezone_format = re.compile(r'\%[zZ]')
_timezone_number_re = re.compile(r'[\+\-](([0-9]{4})|[0-9]{2}\:[0-9]{2})')

_value_error_msg = 'unconverted data remains: '

_time_offset_map = {
        'GMT': 0,
        'EST': -5,
        'EDT': -4,
        #'CST': -6,
        'CDT': -5,
        'MST': -7,
        'MDT': -6,
        'PST': -8,
        'PDT': -7,
        'UT': -7,
    }

class FixedOffset(Offset):
    '''Fixed offset in hours east from UTC.'''

    def __init__(self, offset, name='', is_minute=False):
        super(FixedOffset, self).__init__(offset, name)
        if is_minute:
            self.__offset = timedelta(minutes=offset)
        else:
            self.__offset = timedelta(hours=offset)
        if name == '':
            sign = offset < 0 and '-' or '+'
            self.__name = u"%s%02d%02d" % (sign, abs(offset) / 60., abs(offset) % 60)
        else:
            self.__name = name

    def __repr__(self):
        return self.__name

CST_CN = FixedOffset(8, 'CST')

def add_formatter(s):
    _formatters.append(s)

def _get_time(time_dict, locale='zh-cn'):
    now = datetime.now()
    year = int(time_dict.get('year', now.year))
    if year < 1900:
        # NOTICE here might get wrong year, temporary solution
        year = now.year
    month = int(time_dict.get('month', now.month))
    day = int(time_dict.get('day', now.day))
    hour = int(time_dict.get('hour', now.hour))
    minute = int(time_dict.get('minute', now.minute))
    second = int(time_dict.get('second', now.second))
    dt = datetime(year, month, day, hour, minute, second)
    tz = CST_CN if locale == 'zh-cn' else utc
    dt = dt.replace(tzinfo=tz)
    return _normalize_time(dt.astimezone(utc))

def extract_time(s, locale='zh-cn'):
    '''
    Extract time from string. Use regex to extract by given formats
    '''
    if not s:
        return None
    if not isinstance(s, unicode):
        s = unicode(s, 'utf-8', 'ignore')
    for r in _time_res:
        m = re.search(r, s, re.I)
        if m:
            time_dict = m.groupdict()
            return _get_time(time_dict)
    # can not extract time from string, return None
    return None

def format_time(s, locale='zh-cn'):
    '''
    Receive a string and return a datetime object formatted from the string.
    Use _formatters to format. If no formatter can format the string, return False.
    '''
    if not s:
        return default_time(locale)
    if type(s) in [float, int]:
        return timestamp2datetime(s * 1000)
    for f in _formatters:
        f = re.sub(_timezone_format, '', f).strip()
        zone, zone_str = None, ''
        try:
            dt = datetime.strptime(s, f)
            # If not exception, means no timezone info in string. Need to return
            # a datetime with default timezone that decided by locale.
            now = datetime.utcnow()
            if dt.year == 1900 and dt.month == 1 and dt.day == 1:
                dt = dt.replace(year=now.year,month=now.month,day=now.day)
            elif dt.year == 1900:
                dt = dt.replace(year=now.year)
            tz = CST_CN if locale == 'zh-cn' else utc
            dt = dt.replace(tzinfo=tz)
            return _normalize_time(dt.astimezone(utc))
        except ValueError, err:
            zone, zone_str = _get_timezone('%s' % err, locale)
        if zone and zone_str:
            s = s.replace(zone_str, '').strip()
            dt = datetime.strptime(s, f)
            dt = dt.replace(tzinfo=zone)
            return _normalize_time(dt.astimezone(utc))
    return default_time(locale)

def default_time(locale='zh-cn'):
    '''
    Current UTC time with timezone.
    '''
    dt = datetime.utcnow()
    dt = dt.replace(tzinfo=utc)
    return _normalize_time(dt)

def _default_timezone(locale):
    '''
    Default timezone decided by locale.
    zh-cn: CST.
    en-us: UTC.
    '''
    return CST_CN if locale == 'zh-cn' else utc

def _get_timezone(s, locale):
    '''
    Return a tzinfo object from the given string.
    s can have two format:
      1. with name link GMT/EST.
      2. with time delta like +0800, -0600, -06:30, +06:30.
    '''
    zone_str = s.replace(_value_error_msg, '').strip()
    if re.search(_timezone_number_re, zone_str):
        return _get_timezone_from_delta(zone_str, locale), zone_str
    else:
        return _get_timezone_from_name(zone_str, locale), zone_str

def _get_timezone_from_name(name, locale):
    '''
    Get timezone from timezone name.
    '''
    if name in _time_offset_map:
        return FixedOffset(_time_offset_map[name], name)
    else:
        try:
            return timezone(name)
        except exceptions.UnknownTimeZoneError:
            return _default_timezone(locale)

def _get_timezone_from_delta(delta, locale):
    '''
    Get timezone from timezone delta with UTC time.
    '''
    if delta.startswith('+'):
        delta = delta.replace('+', '')
        return _format_delta(delta, locale)
    elif delta.startswith('-'):
        delta = delta.replace('-', '')
        return _format_delta(delta, locale)
    else:
        return _default_timezone(locale)

def _format_delta(delta, locale, sub=False):
    hour, minute = 0, 0
    try:
        if delta.find(':') != -1:
            h, m = delta.split(':')
            hour = int(h)
            minute = int(m)
        else:
            delta = int(delta)
            hour, minute = delta / 100, delta % 100
        hour, minute = (-hour, -minute) if sub else (hour, minute)
        if minute != 0:
            minute = hour * 60 + minute
            return FixedOffset(minute, "CUSTOM", is_minute=True)
        else:
            return FixedOffset(hour, 'CUSTOM')
    except AttributeError:
        raise
    except Exception:
        return _default_timezone(locale)


def _normalize_time(t):
    '''
    Sometimes the time object formatted form string is invalid, so we need to validate
    the time before return it.
    '''
    now = utc.localize(datetime.utcnow())
    return now if t > now else t

if __name__ == '__main__':
    fmt = '%Y-%m-%d %H:%M:%S %Z%z'
    #t = format_time('2013年08月26日 19:44:56', 'zh-cn')
    #if t:
    #    print t.strftime(fmt)

    # test extract time
    tm = extract_time('2013年08月26日 19:44:56 laiyuan qita dengdeng', 'zh-cn')
    if tm:
        print tm.strftime(fmt)
