'''Extension of MetricsManager to deal with videos, including
   an example of usage on a sample video (downloaded as needed)'''

from __future__ import division
import os
from collections import defaultdict

import numpy as np
import cv2
import pydub

from np_utils.gen_utils import makeifnotexists
from np_utils import split_list_on_condition, identity, groupByFunction, fL
from metric_storage_interface import NpyStorageInterface
from metric_types import (Metric, TimeMetric, SparseTimeMetric, TimeMetric2D,
                          SparseTimeMetric2D, time_inds_cleaner)
from argument_handling import ag, print_metrics_msg
from metrics_manager import MetricsManager

from wxPyGameVideoPlayer import cv2_utils

# Metric types:
METADATA = 'metadata'
AUDIO = 'audio'
VIDEO = 'video'
SPARSE_VIDEO = 'sparse_video'
DERIVED = 'derived'

# Basic metrics names:
VIDEO_NUM_FRAMES = 'video_num_frames'
VIDEO_FPS = 'video_fps'
VIDEO_SAMPLING_INTERVAL = 'video_sampling_interval'

AUDIO_NUM_SAMPLES = 'audio_num_samples'
AUDIO_FPS = 'audio_fps'
AUDIO_SAMPLING_INTERVAL = 'audio_sampling_interval'

AUDIO_TRACE = 'audio_trace'

########################################################################
##                     Metrics processing functions                   ##
########################################################################
# Each metric type (audio, video, etc.) needs to know how to
# handle the arguments passed to it and actually perform the computation
# for each metric. These are their functions. Bum-bum (music plays).

def compute_metadata_metrics(video_file, metrics, verbose=True):
    '''Compute the metadata metrics
       Unlike the other metrics below, this just computes EVERY metadata
       metric every time because they are all small'''
    aud = pydub.AudioSegment.from_file(video_file)
    d = {}
    d[VIDEO_NUM_FRAMES] = cv2_utils.binary_search_end(video_file)
    d[VIDEO_FPS] = cv2_utils.get_frame_rate(video_file)
    d[VIDEO_SAMPLING_INTERVAL] = 1. / d[VIDEO_FPS]
    d[AUDIO_NUM_SAMPLES] = aud.frame_count()
    d[AUDIO_FPS] = aud.frame_rate
    d[AUDIO_SAMPLING_INTERVAL] = 1. / d[AUDIO_FPS]
    return d

def compute_audio_metrics(video_file, metrics, metrics_function_dict, verbose=True):
    audio_fps, a = cv2_utils.mp4_to_array(video_file)
    computed_audio_metrics = {m: metrics_function_dict[m](a) for m in metrics}
    return computed_audio_metrics

def _calc_metric_data(a, last_a, metric_function):
    try:
        return metric_function(a)
    except TypeError:
        return (None if last_a is None else
                metric_function(a, last_a))

def compute_frame_metrics(frame, computed_values_dict,
                          metrics_names, metrics_functions_dict,
                          last_a=None):
    '''Compute metrics for a single frame (grabbed from an existing OpenCV object)
       metrics_names is a list of names for each metrics to compute
       
       Stores results in dictionary of lists, computed_values_dict,
           which must be a defaultdict(list)
       Returns the array data of the frame
       
       optionally takes "last_a", the array of the previous frame
       
       KEEPS None values!'''
    a = np.array(frame)
    for m in metrics_names:
        computed_values_dict[m].append(
          _calc_metric_data(a, last_a, metrics_functions_dict[m]))
    return a

def compute_video_metrics(video_file, metrics, num_frames, metrics_functions_dict, verbose=True):
    '''Handles generating all metrics associated with the video (/image) data
       Depends on all metadata metrics'''
    cap = cv2.VideoCapture(video_file)
    last_a = None
    computed_values_dict = defaultdict(list)
    for i in range(num_frames):
        if verbose:
            print 'process_frame {} out of {}'.format(i, num_frames)
        
        ret, frame = cap.read()
        assert frame is not None, 'Bad frame! (possible binary search issue)'
        last_a = compute_frame_metrics(frame, computed_values_dict, metrics, 
                                       metrics_functions_dict, last_a=last_a)
    
    cap.release()
    
    return computed_values_dict

def compute_video_metrics_sparse(video_file,
                                 metrics,
                                 num_frames,
                                 metrics_functions_dict,
                                 metrics_args_dict, # Has the time information
                                 verbose=True):
    '''Compute video metrics only on certain frames.
       Don't use this for every frame because there is a significant
       (and unavoidable) overhead involved in loading and reloading
       the video file handle each time a frame is grabbed.
       
       metrics_and_index_lists is a list of tuple pairs like:
       (<a metric name string>, <a list of frame numbers>)
       
       Metrics that require two frames (like difference) are not supported (obviously)'''
    if not metrics:
        return {}
    
    index_lists = [time_inds_cleaner(metrics_args_dict[m][0][1], num_frames)
                   for m in metrics]
    all_indices = sorted({int(i) for index_list in index_lists
                                 for i in index_list}) # sorted union of all frames
    assert all_indices[-1] < num_frames, 'Video does not have as many frames as requested!'
    frame_rate = cv2_utils.get_frame_rate(video_file)
    
    computed_values_dict = defaultdict(list)
    for i in all_indices:
        if verbose:
            print 'process_frame {} - last frame {}'.format(i, all_indices[-1])
        
        frame = cv2_utils.get_opencv_frame_as_array(video_file, i, frame_rate)
        metric_names_to_run = [m for m, inds in zip(metrics, index_lists)
                                 if i in inds]
        assert frame is not None, 'Bad frame! (possible binary search issue)'
        compute_frame_metrics(frame, computed_values_dict, metric_names_to_run, 
                              metrics_functions_dict)
                
    return computed_values_dict

def compute_derived_metrics(video_file, metrics, metrics_function_dict, loader, verbose=True):
    computed_derived_metrics = {m: metrics_function_dict[m](loader) for m in metrics}
    return computed_derived_metrics

##########################################################################
## Define MetricsManager and accompanying argument processing functions ##
##########################################################################
# The MetricsManager manages everything for a single video file:
# * perform all computations for individual metrics
# * process metric definitions data (see _METRICS_DEFINITIONS below)
# * interface with the storage interface (save, load)
# * maintain an in-memory cacheing system (metrics_dict)

class VideoMetricsManager(MetricsManager):
    '''Object to manage metrics for a single video file and act as a go-between
       for the storage interface and the individual metric definitions'''
    def __init__(self, filename, storage_interface, metrics_definitions_dict,
                 metrics_dict=None):
        '''Just a way to group some oft-used parameters and provide easy cacheing'''
        MetricsManager.__init__(self, filename, storage_interface,
                                metrics_definitions_dict,
                                metrics_dict=metrics_dict)
    
    def _metrics_compute(self, type_name, compute_function, metrics, verbose, save, *args, **kwds):
        '''Call one of the metric compute functions above
           (passed as the "compute_function" argument)
           Also handles printing messages, caching, and saving'''
        verbose = kwds['verbose'] if 'verbose' in kwds else True # pass "verbose" on to wrapped function
        save = kwds.pop('save', True)                            # but pop "save" and remove it
        _print = lambda msg: print_metrics_msg(msg, metrics, verbose)
        
        if verbose:
            print 'Start computing', type_name, 'metrics'
        
        if metrics:
            _print('Computing the following metrics')
            retval = self.metrics_dict.update(compute_function(
                self.filename, metrics, *args, **kwds))
            _print('Successfully computed')
            if save:
                _print('Saving')
                for m in metrics:
                    self.save_metric(m)
                _print('Saved')
        else:
            _print('No metrics requested, skipping!')
            retval = {}
        
        if verbose:
            print 'Finished computing', type_name, 'metrics'
        
        return retval
    
    def _compute_metadata_metrics(self, metrics, verbose=True, save=True):
        self._metrics_compute(METADATA, compute_metadata_metrics, metrics, verbose, save)
    
    def _compute_audio_metrics(self, metrics, verbose=True, save=True):
        self._metrics_compute(AUDIO, compute_audio_metrics, metrics, verbose, save,
                              self.metric_compute_function)
    
    def _compute_video_metrics(self, metrics, verbose=True, save=True):
        num_frames = self._load_metric(VIDEO_NUM_FRAMES)
        self._metrics_compute(VIDEO, compute_video_metrics, metrics, verbose, save,
                              num_frames, self.metric_compute_function)
    
    def _compute_sparse_video_metrics(self, metrics, verbose=True, save=True):
        num_frames = self._load_metric(VIDEO_NUM_FRAMES)
        self._metrics_compute(SPARSE_VIDEO, compute_video_metrics_sparse, metrics, verbose, save,
                              num_frames, self.metric_compute_function, self.metric_extra_arguments)
    
    def _compute_derived_metrics(self, metrics, verbose=True, save=True):
        for m in metrics: # Do these one-by-one
            self._metrics_compute(DERIVED, compute_derived_metrics, [m], verbose, save,
                                  self.metric_compute_function, self._load_metric)
    
    def compute_metrics(self, metrics, force_resave=False, verbose=True, save=True):
        '''New central processing zone
           Generate new metrics, load existing metrics
           Auto-save, auto-cache, etc'''
        # Determine which metrics already exist (or overwrite them all if force_resave is True)
        if hasattr(self.storage_interface, 'metrics_dir'):
            metrics_dir = (os.path.join(os.path.dirname(self.filename), 'metrics')
                           if self.storage_interface.metrics_dir is None else
                           self.storage_interface.metrics_dir)
            makeifnotexists(metrics_dir)
        exists = (False if force_resave else
                  lambda m: self.storage_interface.exists(self.filename, m))
        existing_metrics, new_metrics = split_list_on_condition(metrics, exists)
        print_metrics_msg('Reload these metrics', existing_metrics, verbose)
        
        # Load all existing metrics
        for m in existing_metrics:
            self._load_metric(m)
        
        # Compute all the new metrics
        grouped_metrics = defaultdict(list,
            groupByFunction(new_metrics, lambda m: self.metric_type[m]))
        
        if verbose:
            print 'Start compute'
        self._compute_metadata_metrics(grouped_metrics[METADATA], verbose=verbose, save=save)
        self._compute_audio_metrics(grouped_metrics[AUDIO], verbose=verbose, save=save)
        self._compute_video_metrics(grouped_metrics[VIDEO], verbose=verbose, save=save)
        self._compute_sparse_video_metrics(grouped_metrics[SPARSE_VIDEO], verbose=verbose, save=save)
        self._compute_derived_metrics(grouped_metrics[DERIVED], verbose=verbose, save=save)
        
        if verbose:
            print 'Finish compute'

########################################################################
#   Create "metrics_definitions" below using the MetricsManager DSL    #
#                                                                      #
# The format is a list where elements must be a list 3-5 elements:     #
#                                                                      #
# 1. NAME:     Unique string name - should be defined as a constant    #
# 2. CLASS:    A subclass of Metric                                    #
# 3. TYPE:     Metric type - must be one of KNOWN_METRIC_TYPES         #
# 4. FUNCTION: (optional) Creation function, role determined by type   #
# 5. ARGS:     (optional) Extra arguments passed to __init__ or load   #
#                                                                      #
# The type defines how the metric will get created (aka the function)  #
# and how it can be used.                                              #
# The creation function means the following for each metric type:      #
#     METADATA: (not used, all hard-coded above)                       #
#     AUDIO: function takes the entire audio trace as an array         #
#     VIDEO: function takes a video frame (image) as an array          #
#            or optionally a pair of images (current & previous frame) #
#     SPARSE_VIDEO: function takes a video frame (image) as an array   #
#                                                                      #
# Extra metric arguments (5) should be created using the "ag" function #
# which stores both positional and keyword arguments for later.        #
# Additionally, any value used as an argument in "ag" passes           #
# through _unpack_step, so it can be:                                  #
#   A. a string specifying a metric to load from the storage interface #
#   B. a number (or an array, or whatever)                             #
#   * a tuple pair combining these:                                    #
#     - a metric string to load                                        #
#     - a number or array that the loaded metric is divided by         #
#                                                                      #
# Sample row:                                                          #
#    ['name', TimeMetric2D, AUDIO, some_function,                      #
#         ag(('thing', 10), ystep=4, ystart=15)]                       #
#                                                                      #
########################################################################

if __name__ == '__main__':
    # Sample file to analyze:
    f = os.path.expanduser('~/sciencecasts-_total_eclipse_of_the_moon.mp4')
    
    if not os.path.exists(f):
        print 'File not available, downloading to ' + f
        import urllib
        url = 'http://www.nasa.gov/downloadable/videos/sciencecasts-_total_eclipse_of_the_moon.mp4'
        urllib.urlretrieve(url, f)
        print 'Finished downloading'
    
    metrics_definitions = [
        #Metadata metrics:
        [VIDEO_FPS, Metric, METADATA],
        [VIDEO_NUM_FRAMES, Metric, METADATA],
        [VIDEO_SAMPLING_INTERVAL, Metric, METADATA],
        [AUDIO_FPS, Metric, METADATA],
        [AUDIO_NUM_SAMPLES, Metric, METADATA],
        [AUDIO_SAMPLING_INTERVAL, Metric, METADATA],
        
        #Other metrics:
        [AUDIO_TRACE, TimeMetric, AUDIO, identity, ag(AUDIO_SAMPLING_INTERVAL)],
    ]
    
    mm = VideoMetricsManager(f, NpyStorageInterface(), metrics_definitions,
                             metrics_dict={})
    mm.get_metrics([VIDEO_NUM_FRAMES,
                    VIDEO_FPS,
                    VIDEO_SAMPLING_INTERVAL,
                    AUDIO_NUM_SAMPLES,
                    AUDIO_FPS,
                    AUDIO_SAMPLING_INTERVAL,
                    AUDIO_TRACE,
                   ],
                  #force_resave=True,
    )
    
    # Prove it worked by plotting the audio from the video :)
    import plt
    plt.ioff()
    plt.plot(mm.get_metrics([AUDIO_TRACE])[AUDIO_TRACE].data)
    plt.show()
