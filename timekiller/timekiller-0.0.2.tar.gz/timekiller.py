import signal
from contextlib import contextmanager
import functools


class TimeoutException(Exception):
    pass


@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


def call(func, max_time, *args, **kwargs):
    with time_limit(max_time):
        return func(*args, **kwargs)


def timeout(max_time):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return call(func, max_time, *args, **kwargs)
        return wrapper
    return decorator
