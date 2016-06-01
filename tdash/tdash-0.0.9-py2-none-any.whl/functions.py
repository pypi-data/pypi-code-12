import time
import functools
import inspect
from generators import count


def retry_n_times(fn, n, exception=Exception, interval=0, on_exception=None, args=(), kwargs={}):
    for n in range(n):
        try:
            return fn(*args, **kwargs)
        except exception as e:
            if interval > 0:
                time.sleep(interval)
            if on_exception:
                on_exception(e)


###
# Function composition is a way of combining functions such that the result of each function
# is passed as the argument of the next function.
# For example, the composition of two functions f and g is denoted f(g(x))
###
def compose(*funcs): return lambda x: reduce(lambda v, f: f(v), reversed(funcs), x)

###
# Sometimes when writing functional code it's handy to raise an exception
# there doesnt seem to be a built in function that raises an exception (raise is a statememt)
# e.g. you cannot write lambda x: raise Exception('bugger')
# you can howerver write lambda x: _.raise(Exception('bugger'))
###
def raise_ex(exception):
    raise exception

###
# Like partial but it safely ignores excess arguments and keywords!
###
def safe_partial(fn, *args, **kwargs):

    fn_args, fn_varargs, fn_keywords, __ = inspect.getargspec(fn)

    if fn_keywords is None:
        kwargs = { k: v for k,v in kwargs.items() if k in fn_args }

    available_arguments =  len(fn_args) - count((k for k in kwargs.keys() if k in fn_args ))
    if fn_varargs is None and len(args) > available_arguments:
        # Throw away some arguments!
        args = args[0:len(fn_args)]

    return functools.partial(fn, *args, **kwargs)

###
# Convenience method for wrapping a function on the fly.
# Wrapper function takes a function, which is the thing it is wrapping with its args already curried in as first argument
# you cannot mess therefore with the arguments. But you can decide to execute it or not and do stuff before or after
###
def wrap(fn, wrapper):
    @functools.wraps(fn)
    def wrap(*args, **kwds):
        next = functools.partial(fn, *args, **kwds)
        wrapper_args = (next,) + args
        return safe_partial(wrapper, *wrapper_args, **kwds)()
    return wrap


###
# Method for exception handling on the fly.
# n.b. executes f
# n.b. tightly bound to on_exception
###
def attempt(fn, on_exception, catch_exception=Exception):
    try:
        return fn()
    except catch_exception as e:
        return on_exception(e)

###
# Convenience method.
# Returns a function wrapped so that exceptions are handled and caught with default method
# default method receives the thrown exception as arg
###
def on_exception(fn, on_exception, catch_exception=Exception):
    return wrap(fn, lambda f: attempt(f, on_exception=on_exception, catch_exception=catch_exception))


def result(fn_or_value, *args, **kwargs):
    """
     If argument is a function execute it. If it is a value, return it.
     Useful for handling lazy execution of default cases:
     e.g.
     _.result(some_dict.get(key, lambda: ))
    :param fn_or_value:
    :param args:
    :param kwargs:
    :return:
    """
    if inspect.isfunction(fn_or_value):
        return safe_partial(fn_or_value, *args, **kwargs)()
    return fn_or_value


###
# Works with class methods when defined outside the class
# Does not work with unhashable arguments; hence does not work with **kwargs, which is a dict
# Examples: 1. Fibonacci
# @memoize
# def fib(n):
# '''Returns the nth number in the Fibonacci series (n > 0)'''
#     return 1 if (n == 1 or n == 2) else (fib(n-1) + fib(n-2))
# print fib(5)
# 2. Sum
# @memoize
# def mult(a, b):
#     return a * b
###
def memoize(f):
    """
    Decorator to memoize a function taking one or more arguments.
    Uses per-instance cache. Does not have a method to reset cache.

    :param decorated_function: Function to be decorated
    : return:
    """
    cache = {}
    def decorated_function(*args):
        if args in cache:
            return cache[args]
        else:
            cache[args] = f(*args)
            return cache[args]
    return decorated_function