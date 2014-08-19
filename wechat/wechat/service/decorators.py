#!/usr/bin/env python
# coding: utf-8
"""
Created On Jul 2, 2014

@author: jwang
"""
import sys
import logging

from functools import wraps
from pymongo.errors import InvalidName
from weibonews.utils.web.errors import parameter_error, internal_server_error
from wechat.utils.exceptions import ParameterError, FormatterError, RequiredNoDefaultError, RequiredLackedError, MethodError

_LOGGER = logging.getLogger('weibonews.wechat')


def catch_except(func):
    """
    Indicating a method process general exception.
    """
    @wraps(func)
    def _catch_except(*args, **kwargs):
        """
        catch exception raised by func
        """
        try:
            request = args[0]
            return func(*args, **kwargs)
        except (FormatterError, RequiredNoDefaultError, RequiredLackedError, MethodError, ParameterError), err:
            _LOGGER.error(err)
            return parameter_error(request, str(err))
        except InvalidName, err:
            msg = 'keys in document error: %s' % err
            _LOGGER.exception(msg)
            return internal_server_error(request, msg, sys.exc_info())
        except Exception, err:
            _LOGGER.exception(err)
            return internal_server_error(request, err, sys.exc_info())
    return _catch_except

