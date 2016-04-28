'''The actual metrics manager class
   Coordinates everything about the metrics (computation, storage, etc)
   
   Extend the class to implement specific behaviors for metric types'''

import numpy as np

from np_utils import linrange, split_list_on_condition, identity, groupByFunction, doublewrap, rotate_dict_of_lists

from argument_handling import ag, process_args
from metric_storage_interface import NpyStorageInterface

#def _call_keys(keys, function_dict):
#    return {function_dict[k]() for k in keys}

def _assert_no_diff(a, b, message=None):
    if message is None:
        message = 'Cannot compute the following metrics, no specification exists'
    diff = set(a) - set(b)
    assert not diff, message + ': {}'.format(diff)

class MetricsManager(object):
    '''Object to manage metrics for a single file and act as a go-between
       for the storage interface and the individual metric definitions
       
       * performs all computations for individual metrics
       * processes metric definitions data (see __init__)
       * interfaces with the storage interface (save, load)
       * maintains an in-memory cacheing system (metrics_dict)'''
    def __init__(self, filename, storage_interface, metrics_definitions,
                 metrics_dict=None):
        '''Just a way to group some oft-used parameters and provide easy cacheing
           
           storage_interface must be a MetricsStorageInterface
           metrics_definitions must be an iterable of iterables with
           elements like the following:
           [name,             # A unique string used to identify the metric
            class,            # A sub-class of Metric (see metric_types.py)
            type,             # A string used to route the metric to the
                              # right kind of processing
            compute function, # A function that computes the metric (optional)
            extra arguments]  # Any other arguments to the Metric sub-class
                              # past the standard two (name, data) -- (optional)
            
            metrics_definitions is list of lists of 3-5 elements
            
            These elements are:
              1. A unique name to identify the metric
              2. A metric class (defines how the metric will get created and how it can be used)
              3. A metric type
              4. (optional) A metric creation function (exact role is defined by the metric type)
              5. (optional) Any extra metric arguments (passed to .__init__ or .load)
            
            The extra metric argument (5) should be created using the "ag" function
            which stores both positional and keyword arguments for later.
            Additionally, any value used as an argument in "ag" passes
            through _unpack_val, so it can be:
              A. a string specifying a metric to load from the storage interface
              B. a number (or an array, or whatever)
              * a tuple pair combining these:
                - a metric string to load
                - a number or array that the loaded metric is divided by
            
            Sample row:
              {'name': [TimeMetric2D, some_function, ag(('time_thing', 10), ystep=4, ystart=15)]
           '''
        self.filename = filename
        self.storage_interface = storage_interface
        
        # Generate the four dictionaries from the metrics definitions:
        # class, type, compute function, and extra arguments
        _metrics_definitions_dict = {i[0]: i[1:] for i in metrics_definitions}
        (self.metric_class,
         self.metric_type,
         self.metric_compute_function,
         self.metric_extra_arguments) = rotate_dict_of_lists(_metrics_definitions_dict)
        
        self.metrics_dict = metrics_dict # the cache

    def _load_metric(self, metric_name):
        '''Load metric data from the cache or storage interface
           Cache any metrics in metrics_dict (as long as it is not None)'''
        d = self.metrics_dict
        if d is None or metric_name not in d:
            v = self.storage_interface.get_metric(self.filename, metric_name)
            if d is None:
                return v
            d[metric_name] = v
        return d[metric_name]

    def generate_metric_args(self, metric_name, verify_usage=True):
        return process_args(self.metric_class[metric_name],
                            self.metric_extra_arguments.get(metric_name, None),
                            self._load_metric,
                            verify_usage=verify_usage)

    # I think this is about as simple as it gets:
    def build_metric(self, metric_name, metric_data):
        '''Build a metric class'''
        args, kwds = self.generate_metric_args(metric_name)
        return self.metric_class[metric_name](metric_name, metric_data, *args, **kwds)

    def load_metric(self, metric_name):
        '''Load a metric and build a metric class'''
        metric_data = self._load_metric(metric_name)
        return self.build_metric(metric_name, metric_data)
    
    def save_metric(self, metric_name):
        self.storage_interface.save_metric(self.filename, metric_name,
                                           self.metrics_dict[metric_name])
    
    def compute_metrics(self, metrics, force_resave=False, use_print=True):
        '''New central processing zone
           Generate new metrics, load existing metrics
           Auto-save, auto-cache, etc'''
        pass
    
    def get_metrics(self, metrics, force_resave=False):
        '''Generate and cache metrics and then build metrics classes'''
        self.compute_metrics(metrics, force_resave)
        return {m: self.load_metric(m) for m in metrics}

# "Pseudo-code" basic example usage:
# find_color = lambda img_arr: np.mean(img_arr, axis=0)
# METRICS_DEFINITIONS = [['extension', Metric, 'metadata'],
#                        ['color', Metric, 'image', find_color],
#                        ['mean_value', Metric, 'image', np.mean]]
# f = '/somefile.img'
# mm = VideoMetricsManager(f, NpyStorageInterface(), METRICS_DEFINITIONS)
# mm.get_metrics(['extension', 'color', 'mean_value'],
#                #force_resave=True,
# )
