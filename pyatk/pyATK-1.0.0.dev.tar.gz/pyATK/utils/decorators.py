import time
from contextlib import ContextDecorator


def not_implemented(func):
    raise NotImplementedError("Function " + func.__name__ + " is not implemented!")
        
    
def windows_only(func):
    import os

    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
        
    if os.name == "nt":
        return wrapper
    raise Exception("Not available on " + os.name + " platform")

    
def posix_only(func):
    import os

    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
        
    if os.name == "nt":
        return wrapper
    raise Exception("Not available on " + os.name + " platform")
    
    
def timeout(seconds=10, msg="Function timed out"):
    import signal

    class TimeoutException(Exception):
        def __init__(self, message):
            self.message = message

        def __str__(self):
            return self.message

    def callback(signum, frame):
        raise TimeoutException(msg)

    def wrapper(func, *args, **kwargs):
        signal.signal(signal.SIGALRM, callback)
        signal.alarm(seconds)
        result = None
        try:
            result = func(*args, **kwargs)
        except TimeoutException as e:
            print(e)
            
        finally:
            signal.alarm(0)
        return result
    return wrapper


class timeit(ContextDecorator):
    def __init__(self):
        self.start = None
        self.end = None
        
    def __enter__(self):
        self.start = time.time()

    def __exit__(self, *exc):
        self.end = time.time()
        print("Execution time is " + str(self.end - self.start) + " seconds")
        
    
def retry(nb=3, delay=1):
    def decorator(f):
        def wrapper(*args, **kwargs):
            for i in range(0, nb):
                print("Try " + str(i+1) + " out of " + str(nb))
                return_value = f(*args, **kwargs)
                if return_value is True:
                    print("Success!")
                    return True
                time.sleep(delay)
            print("Out of tires...")
            return False
        return wrapper
    return decorator
