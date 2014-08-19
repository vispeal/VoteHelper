import calendar
from django.utils import simplejson
from django.http import HttpResponse
from wechat.utils import exceptions


def cursor_to_array(cursor):
    return [i for i in cursor]


def datetime2timestamp(dt):
    '''
    Converts a datetime object to UNIX timestamp in milliseconds.
    '''
    if hasattr(dt, 'utctimetuple'):
        t = calendar.timegm(dt.utctimetuple())
        timestamp = int(t) + dt.microsecond / 1000000.0
        return timestamp * 1000
    return dt


def response_json(obj):
    content = simplejson.dumps(obj, ensure_ascii=False)
    response = HttpResponse(content, content_type='application/json; charset=utf-8')
    return response


def get_parameter(request, name, required=False, default=None, formatter=None, method='GET'):
    '''
    Get parameter of request.
    '''
    if required and default is not None:
        raise exceptions.RequiredNoDefaultError(name)
    if method == 'GET':
        if required:
            value = request.GET.get(name)
        else:
            value = request.GET.get(name, default)
    elif method == 'POST':
        if required:
            value = request.POST.get(name)
        else:
            value = request.POST.get(name, default)
    elif method == 'META':
        if required:
            value = request.META.get(name)
        else:
            value = request.META.get(name, default)
    else:
        raise exceptions.MethodError(method)
    if required and value is None:
        raise exceptions.RequiredLackedError(name)
    if value is not None and formatter:
        try:
            return formatter(value)
        except Exception, err:
            raise exceptions.FormatterError('parameter %s format %s failed: %s.' % (name, value, str(err)))
    return value
