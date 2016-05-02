'''Generic storage interfaces with a common api
   So far, only file-based interfaces are implemented (.json and .npy)
   
   Here, metrics are for a specific file (root),
   such as a large binary or video file'''

import os
import numpy as np

try:
    import simplejson as json
except ImportError:
    import json

class MetricsStorageInterface(object):
    def __init__(self):
        pass
    
    def exists(self, root_file, metric_name):
        pass
    
    def save_metric(self, root_file, metric_name):
        pass
    
    def get_metric(self, root_file, metric_name):
        pass

class FileBasedStorageInterface(MetricsStorageInterface):
    def __init__(self, file_ext):
        self.file_ext=file_ext

    def _get_metric_filename(self, root_file, metric_name):
        '''Rework the filepath of the root file into a filepath to a metric'''
        root_dir, root_name = os.path.split(root_file)
        metrics_dir = os.path.join(root_dir, 'metrics')
        new_name = root_name.replace('.', '_') + '_' + metric_name + self.file_ext
        filename = os.path.join(metrics_dir, new_name)
        return filename
    
    def exists(self, root_file, metric_name):
        '''Test if a given metric already exists'''
        filepath = self._get_metric_filename(root_file, metric_name)
        return os.path.exists(filepath)
    
    def get_metric(self, root_file, metric_name):
        filepath = self._get_metric_filename(root_file, metric_name)
        # load the data
    
    def save_metric(self, root_file, metric_name, metric_data):
        filepath = self._get_metric_filename(root_file, metric_name)
        # save the data
    
# Json is a less-than-ideal storage format for binary data, but it's easy:
def _to_flat(x):
    return (x.tolist() if type(x) == np.ndarray else x)

class JsonStorageInterface(FileBasedStorageInterface):
    def __init__(self):
        FileBasedStorageInterface.__init__(self, file_ext='.json')
    
    def get_metric(self, root_file, metric_name):
        filepath = self._get_metric_filename(root_file, metric_name)
        return json.load(filepath)
    
    def save_metric(self, root_file, metric_name, metric_data):
        filepath = self._get_metric_filename(root_file, metric_name)
        json.dump(filepath, _to_flat(metric_data)) # Force numpy arrays to lists

# Npy is a actually a great storage format for this:
class NpyStorageInterface(FileBasedStorageInterface):
    def __init__(self):
        FileBasedStorageInterface.__init__(self, file_ext='.npy')
    
    def get_metric(self, root_file, metric_name):
        filepath = self._get_metric_filename(root_file, metric_name)
        return np.load(filepath)
    
    def save_metric(self, root_file, metric_name, metric_data):
        filepath = self._get_metric_filename(root_file, metric_name)
        np.save(filepath, metric_data)

# This could work by storing a "document" version of a number of different
# metrics in a single file which would cut down on file usage, but make
# it harder to update with new metrics.
##class NpyConsolidatedStorageInterface(MetricsStorageInterface)
#class NpzStorageInterface(MetricsStorageInterface)
# Pytables might be another alternative.
##class PyTablesStorageInterface(MetricsStorageInterface)

##    ........eventually probably a better way for some applications:)
#class SQLStorageInterface(MetricsStorageInterface):

if __name__ == '__main__':
    pass
