'''
Created on Jan 31, 2013

@author: fli
'''
import logging
from time import time
from weibonews.utils.format import simple_params
from functools import wraps

PERF_LOGGER = logging.getLogger('weibonews.perf')

def perf_logging(func):
    """
    Record the performance of each method call.
    """
    @wraps(func)
    def perf_logged(*args, **kwargs):
        argnames = func.func_code.co_varnames[:func.func_code.co_argcount]
        fname = func.func_name
        module_name = func.func_code.co_filename.split("/")[-1].split('.')[0]
        entries = simple_params(zip(argnames, args) + kwargs.items())
        msg = '%s.%s(%s)' % (module_name, fname, ','.join('%s=%s' % entry for entry in entries))

        logging.debug(msg)
        start_time = time()
        ret_val = func(*args, **kwargs)
        end_time = time()
        PERF_LOGGER.debug('%s <- %s ms.' % (msg, 1000 * (end_time - start_time)))
        return ret_val
    return perf_logged
