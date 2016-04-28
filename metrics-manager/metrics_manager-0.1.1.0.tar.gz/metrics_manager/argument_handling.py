'''Argument processing helper functions'''

from functools import partial, wraps

import numpy as np

from np_utils.func_utils import get_function_arg_names_and_kwd_values

def ag(*args, **kwds):
    '''Capture and return all args and kwds for future use in another function'''
    return args, kwds

def _unpack_val(load_fun, x):
    '''Check for special cases, return a cleaned value for x
       
       x can be:
       A. a string specifying a metric to load from the storage interface
       B. a number (or an array, or whatever)
          * a tuple pair combining these:
            - a metric string to load
            - a number or array that the loaded metric is divided by'''
    #Optionally unpack a tuple:
    numerical_types = [int, long, float, np.ndarray]
    try:
        if type(x[0]) is str and type(x[1]) in numerical_types:
            x, multiplier = x
        else:
            raise
    except:
        x, multiplier = x, 1
    
    #Optionally load a metric using the storage interface:
    if type(x) is str:
        x = load_fun(x)
    
    return x / multiplier

def process_args(metric_class, some_ag, load_fun, verify_usage=True):
    if some_ag is None:
        return [], {}
    
    # Grab the actual args and kwds
    unpack = partial(_unpack_val, load_fun)
    args, kwds = some_ag
    args = map(unpack, args)
    kwds = {k: unpack(v) for k, v in kwds.iteritems()}
    
    if verify_usage:
        nargs = len(args)
        arg_names, metric_defaults = get_function_arg_names_and_kwd_values(metric_class.__init__)
        metric_args = arg_names[3:] # (ignore first 3 values: self, name, and data)
        max_nargs = len(metric_args)
        min_nargs = max_nargs - len(metric_defaults)
        
        assert min_nargs <= nargs <= max_nargs, 'Not enough arguments!'
        metrics_kwds_active = metric_args[nargs:]
        assert not set(kwds.keys()) - set(metrics_kwds_active), 'Unknown (or reused) keyword!'
        
        #kwds_defaults_dict = dict(zip(metric_args[-len(metric_defaults):], metric_defaults))
    
    return args, kwds

def print_metrics_msg(msg, metrics, use_print):
    if use_print and metrics:
        print msg+':', ', '.join(metrics)

def enable_metric_save(f):
    @wraps(f)
    def newf(self, metrics, save=True, use_print=True):
        _print = lambda msg: print_metrics_msg(msg, metrics, use_print)
        if metrics:
            _print('Computing the following metrics')
            retval = f(self, metrics)
            _print('Successfully computed')
            if save:
                _print('Saving')
                for m in metrics:
                    self.save_metric(m)
                _print('Saved')
        else:
            _print('No metrics requested, skipping!')
            retval = {}
        
        return retval
    return newf
