'''Argument processing helper functions'''

from functools import partial
import toposort

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
            - a number or array that the loaded metric is multiplied by'''
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
    
    return x * multiplier

def process_args(metric_class, some_ag, load_fun, verify_usage=True):
    '''Unpack the arguments, load any metrics needed for cumputation
       using the load_fun, and compute any ratios requested (tuples).
       If "verify_usage" True, also ensure that the arguments to the
       metric class are acceptable.
       (This is essentially performs the delayed computation as defined
        in the metric_definitions DSL)
       '''
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

EXTRA_ARGS_INDEX = 4

def find_metrics_dependencies(metric_definitions):
    '''Build up a list of dependencies from the metrics definitions
       using the "extra arguments"
       This unpacks the ag arguments and looks for any strings,
       using the fact that any ag can contain a string, a tuple pair,
       or something else.'''
    metrics_dependencies = {}
    for m, d in metric_definitions.iteritems():
        if len(d) <= EXTRA_ARGS_INDEX:
            metrics_dependencies[m] = {} # No dependencies
        else:
            args, kwds = d[EXTRA_ARGS_INDEX] # the extra arguments
            all_args = list(args) + kwds.values()
            all_args = [i[0] if type(i) is tuple else i
                        for i in all_args]
            deps_set = {i for i in all_args
                        if type(i) is string}
            metrics_dependencies[m] = deps_set

    return metrics_dependencies

def filter_metric_definitions(metric_definitions, metrics):
    '''Filter the metric_definitions to keep only the entries necessary
       for computing the given metrics (those metrics + dependencies).'''
    metrics_dependencies = find_metrics_dependencies(metrics_definitions)
    
    new_metrics = set(metrics)
    relevant_metrics = set()
    for i in range(len(metric_definitions)): # outer loop, maximum number of iterations
        if not new_metrics:
            break
        
        m = new_metrics.pop()
        relevant_metrics.add(m)
        new_metrics.update(metrics_dependencies[m] - relevant_metrics)
    
    return {k: v for k, v in metric_definitions.iteritems()
                 if k in relevant_metrics}

def toposort_flatten_checking(d, sort=False):
    '''Essentially just toposort_flatten, but with checking for
       self-referential dependencies and defaulting to sort=False
       to preserves order when possible'''
    for k, v in d.iteritems():
        assert k not in v, 'Self-referencing dependency: {}'.format(k)
    return toposort.toposort_flatten(d, sort=sort)

def metrics_dependency_sort(metrics, metrics_definitions):
    '''Given a list of metrics, return a "computation plan",
       an ordered list of all metrics needed to compute these metrics
       without errors (using toposort package).
       This also ensures that there are no cyclic dependencies.'''
    filtered_definitions = filter_metric_definitions(metric_definitions, metrics)
    minimal_dependencies = find_metrics_dependencies(filtered_definitions)
    return toposort_flatten_checking(minimal_dependencies)

def print_metrics_msg(msg, metrics, use_print):
    if use_print and metrics:
        print msg+':', ', '.join(metrics)
