def first(iterable):
    if iterable is not None and len(iterable) != 0:
        return iterable[0]


def attach_method(fn, obj, method_name=None):
    method_name = fn.__name__ if method_name is None else method_name
    setattr(obj, method_name, bind(fn, obj))


def bind(fn, obj):
    return fn.__get__(obj)


def partial_left(fn, *args):
    """Set default arguments from the left of the given function."""
    def f(*rest, **kwargs):
        return fn(*(args + rest), **kwargs)
    return f


def partial_right(fn, *rest):
    """Set default arguments from the right of the given function."""
    def f(*args, **kwargs):
        return fn(*(args + rest), **kwargs)
    return f


def compose(a, b):
    """Pass the return value of b to a."""
    def f(*args, **kwargs):
        return a(b(*args, **kwargs))
    return f


def sequence(a, b):
    """Pass return value of a to b."""
    def f(*args, **kwargs):
        return b(a(*args, **kwargs))
    return f


def once(fn):
    """Call this function once throught the lifetime of the script"""
    done = False

    def newFn(*args, **kwargs):
        # grab variable stored in closure
        nonlocal done
        if not done:
            done = True
            return fn(*args, **kwargs)
    return newFn


def maybe(fn, test=None, n=1):
    """Call fn if and only of some first n arguments pass the given test.

    The test checks if an argument is None by default.
    """
    test = test if test is not None else lambda x: x is not None

    def newFn(*args, **kwargs):
        if len(args) < n:
            return
        else:
            all_args = args[:n]
            if all(map(test, all_args)):
                return fn(*args, **kwargs)
    return newFn
