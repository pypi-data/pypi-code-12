from functools import wraps
from time import time

def measure_time(name=None):
    def decorator(func):
        called = name if name else func.__name__
        @wraps(func)
        def func_wrapper(*args, **kwargs):
            t0 = time()
            result = func(*args, **kwargs)
            t = time() - t0
            print called, t
            return result
        return func_wrapper
    return decorator