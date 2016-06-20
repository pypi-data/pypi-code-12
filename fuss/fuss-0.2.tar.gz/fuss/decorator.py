"""fuss module.

It implements basic functionality of benchmarking.
"""
import time


def measure(func):
    """Wrapper to fuss any function."""
    def calculate(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        total_time = (end_time - start_time) * 1000
        print ("Function: {name} took {t} ms").format(name=func.__name__,
                                                      t=total_time)
        return result
    return calculate
