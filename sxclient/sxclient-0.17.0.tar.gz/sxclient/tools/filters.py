'''
Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: Apache 2.0, see LICENSE for more details.
'''
from sxclient.defaults import FILTER_NAME_TO_UUID

__all__ = ['list_filters', 'generate_poll_times']


def list_filters():
    '''Return a list of available filters' names.'''
    return FILTER_NAME_TO_UUID.keys()


def generate_poll_times(start, end, steps):
    '''
    Generate poll times from between start and end bounds.

    First yield 'steps' number of times evenly distributed between the bounds,
    afterwards yield end continuously.
    '''
    if start < 0 or end < 0:
        raise ValueError('start and end should be non-negative')
    start = float(start)
    end = float(end)
    if steps > 1:
        incr = (end - start) / (steps - 1)
        current_time = start
        for _ in xrange(steps-1):
            yield current_time
            current_time += incr
    while True:
        yield end
