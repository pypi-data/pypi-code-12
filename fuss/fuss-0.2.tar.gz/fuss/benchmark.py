"""benchmarking function module.

It calculates time taken to exexute any function.
"""
import time
import types


def benchmark(func):
    """Wrapper to fuss any function."""
    result = None
    if isinstance(func, types.FunctionType):
        start_time = time.time()
        result = func()
        total_time = (time.time() - start_time) * 1000
        print ("Function: {name} took {t} ms").format(name=func.__name__,
                                                      t=total_time)
    return result
