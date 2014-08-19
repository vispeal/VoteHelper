from weibonews.utils.web.errors import parameter_error

def get_optional_parameter(request, name, default=None, formatter=None, method='GET'):
    '''
    Get optional parameter of http request
    '''
    if method == 'GET':
        value = request.GET.get(name, default)
    else:
        value = request.POST.get(name, default)
    if value is not None and formatter:
        try:
            value = formatter(value)
        except:
            if default is None:
                return None, parameter_error(request, name)
            else:
                return default, None
    return value, None
