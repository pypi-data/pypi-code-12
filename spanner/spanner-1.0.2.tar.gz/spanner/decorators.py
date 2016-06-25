import functools
import inspect


def singleton(cls):
    """
    Override class constructor to enforce singleton
    """
    class Singleton:
        def __init__(self):
            self.cls = cls
            self.instance = None

        def __call__(self, *args, **kwargs):
            if not self.instance:
                self.instance = self.cls(*args, **kwargs)
            return self.instance

    s = Singleton()

    @functools.wraps(cls)
    def wrapped(*args, **kwargs):
        return s(*args, **kwargs)

    return wrapped


def memoize(f):
    """
    Cache return values by argument list so the wrapped
    function is never invoked more than once for any
    unique argument set.

    Warning: there is no bound on the amount of memory used to cache these
    values, so this may not be appropriate for functions that return large
    amounts of data.
    """
    class Memoized(dict):
        def __call__(self, *args, **kwargs):
            return self[(args, str(kwargs))]

        def __missing__(self, key):
            args, kwargs = key
            kwargs = eval(kwargs)
            ret = self[key] = f(*args, **kwargs)
            return ret

    m = Memoized()

    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        return m(*args, **kwargs)

    return wrapped


def validate_args(*expected_types):
    """
    Validate argument function types

    Usage:
    @validate_args(int, str, int)
    def foo(a, b, c):
        ...
    """
    def decorator_switcheroo(function_to_validate):
        arg_names = inspect.getargspec(function_to_validate).args
        # default values (if any)
        defaults = inspect.getargspec(function_to_validate).defaults
        if defaults:
            kwarg_to_default = dict(zip(arg_names[-len(defaults):], defaults))

        @functools.wraps(function_to_validate)
        def wrapped_function(*args, **kwargs):

            if len(arg_names) != len(expected_types):
                msg = 'Please provide expected types for all arguments for function {function}()' \
                      .format(function=function_to_validate.func_name)
                raise RuntimeError(msg)

            # non-keyword args - can count on the ordering of these arguments
            arg_values = list(args)

            # can't count on order of kwargs, so grab them by ordered arg nmae
            for kwarg_name in arg_names[len(args):]:
                arg_values.append(kwargs.get(kwarg_name, kwarg_to_default[kwarg_name]))

            for arg_name, value, expected_type in zip(arg_names, arg_values, expected_types):
                # Allow defaulted None values regardless of expected type
                if value is None and arg_name in kwarg_to_default and kwarg_to_default[arg_name] is None:
                    continue

                if not isinstance(value, expected_type):
                    msg = 'Expected {expected_type} for argument "{arg}" in call to {function}(); '\
                          'received {actual_type} ({val})' \
                          .format(expected_type=expected_type, arg=arg_name, function=function_to_validate.func_name,
                                  val=value, actual_type=type(value))
                    raise RuntimeError(msg)

            return function_to_validate(*args, **kwargs)
        return wrapped_function
    return decorator_switcheroo
