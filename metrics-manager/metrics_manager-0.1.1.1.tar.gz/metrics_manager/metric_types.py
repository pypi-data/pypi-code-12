'''Generic metric types for potentially temporal data:
   Metric: Simple (static),
   TimeMetric: time-based (has a time axis) -- assumed to be uniform
   SparseTimeMetric: time-based, non-uniform
   TimeMetric2D: 2D+time data'''

import os
import numpy as np

# Especially important for external functions (like plotting)
def get_time_axis(arr, frame_rate, start_frame=0):
    '''Just a simple wrapper around np.arange to make constructing
       uniform time axes easier'''
    return start_frame + np.arange(len(arr)) * frame_rate

def time_inds_cleaner(time_inds, length):
    '''If time_inds is a singleton (integer) use it as a
       downsampling factor instead'''
    return (np.array(time_inds) if hasattr(time_inds, '__len__') else
            np.arange(0, length, time_inds))


class Metric(object):
    def __init__(self, name, data):
        self.name = name
        self.data = data

class TimeMetric(Metric):
    def __init__(self, name, arr, step, start=0):
        Metric.__init__(self, name, arr)
        self.start = start
        self.step = step
        self.time_axis = get_time_axis(arr, step, start)
        self.length = len(arr)

# I might need this, but I have no idea why I would!
#class ShiftedTimeMetric(object):
#    def __init__(self, name, arr, step, start=0):

class SparseTimeMetric(TimeMetric):
    def __init__(self, name, arr, step, time_inds):
        TimeMetric.__init__(self, name, arr, step)
        self.time_inds = time_inds_cleaner(time_inds, self.length)
        self.sparse_time_axis = self.time_axis[self.time_inds]

class TimeMetric2D(TimeMetric):
    def __init__(self, name, arr2d, tstep, ystep=1, tstart=0, ystart=0):
        TimeMetric.__init__(self, name, arr2d, tstep, tstart)
        
        arr0 = arr2d[0] if self.length else []
        self.ylength = len(arr0)
        self.y_axis = get_time_axis(arr0, ystep, ystart)
        
        self.tstart, self.tstep = tstart, tstep
        self.ystart, self.ystep = ystart, ystep
        self.tstop = tstart + tstep * self.length
        self.ystop = ystart + ystep * self.ylength
        
        self.extent = [self.tstart, self.tstop,
                       self.ystart, self.ystop] # needed for passing to imshow

class SparseTimeMetric2D(TimeMetric):
    def __init__(self, name, arr2d, tstep, time_inds, ystep=1, ystart=0):
        TimeMetric2D.__init__(self, name, arr2d, tstep, ystep=ystep, ystart=ystart)
        self.time_inds = time_inds_cleaner(time_inds, self.length)
        self.sparse_time_axis = self.time_axis[self.time_inds]

if __name__ == '__main__':
    pass
