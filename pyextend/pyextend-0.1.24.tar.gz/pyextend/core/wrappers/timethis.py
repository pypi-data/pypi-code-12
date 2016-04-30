# coding: utf-8
"""
    pyextend.core.wrappers.timethis
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    pyextend core wrappers timethis wrapper

    :copyright: (c) 2016 by Vito.
    :license: GNU, see LICENSE for more details.
"""

import sys
import time
import functools

__all__ = ['timethis']

if sys.version_info < (3, 3):
    _time_perf_counter = time.clock 
else:
    _time_perf_counter = time.perf_counter


def timethis(func):
    """A wrapper use for timeit."""
    func_module, func_name = func.__module__, func.__name__

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = _time_perf_counter()
        r = func(*args, **kwargs)
        end = _time_perf_counter()
        print('timethis : <{}.{}> : {}'.format(func_module, func_name, end - start))
        return r
    return wrapper

if __name__ == "__main__":
    from math import sqrt

    def compute_roots(nums):
        result = []
        result_append = result.append
        for n in nums:
            result_append(sqrt(n))
        return result

    @timethis
    def test():
        nums = range(100000)
        for n in range(100):
            r = compute_roots(nums)

    test()
    timethis(lambda: [x for x in range(100000)])()
