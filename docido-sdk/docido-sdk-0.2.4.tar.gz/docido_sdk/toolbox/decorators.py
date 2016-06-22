
import functools
import inspect
import sys


class lazy(object):
    """A lazily-evaluated attribute.

    :since: 1.0
    """

    def __init__(self, fn):
        self.fn = fn
        functools.update_wrapper(self, fn)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        if self.fn.__name__ in instance.__dict__:
            return instance.__dict__[self.fn.__name__]
        result = self.fn(instance)
        instance.__dict__[self.fn.__name__] = result
        return result

    def __set__(self, instance, value):
        instance.__dict__[self.fn.__name__] = value

    def __delete__(self, instance):
        del instance.__dict__[self.fn.__name__]


def decorate_instance_methods(obj, decorator, includes=None, excludes=None):
    """Decorator instance methods of an object.

    :param obj: Python object whose instance methods have to be decorated
    :param decorator:
      instance method decorator.
      >>> def decorate(name, f):
      >>>   def __wrap(*args, **kwargs)
      >>>     print '--> entering instance method {}'.format(name)
      >>>     eax = f(*args, **kwargs)
      >>>     print '<-- leaving instance method {}'.format(name)

    :param string list includes:
      restrict wrapped instance methods. Default is `None` meaning
      that all instance method are wrapped.
    :param string list excludes:
      used to prevent some instance methods to be wrapped. Default is `None`

    :return: new class that inherits the `clazz` specified in parameter.
    """
    class InstanceMethodDecorator(object):
        def __getattribute__(self, name):
            value = obj.__getattribute__(name)
            if excludes and name in excludes:
                return value
            if includes and name not in includes:
                return value
            if inspect.ismethod(value):
                value = decorator(name, value)
            return value
    return InstanceMethodDecorator()


def reraise(clazz):
    """ Decorator catching every exception that might be raised by wrapped
    function and raise another exception instead.
    Exception initially raised is passed in first argument of the raised
    exception.

    :param: Exception class: clazz:
      Python exception class to raise
    """
    def _decorator(f):
        @functools.wraps(f)
        def _wrap(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                raise clazz(e), None, sys.exc_info()[2]
        return _wrap
    return _decorator
