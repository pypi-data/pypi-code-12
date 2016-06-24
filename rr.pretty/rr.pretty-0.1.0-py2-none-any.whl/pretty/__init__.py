"""
Utility functions to help in the creation of nicer repr() and str() representations for objects.
"""
from __future__ import absolute_import
from functools import partial
import pkgutil


__version__ = pkgutil.get_data(__name__, "VERSION").strip()
DEFAULT_FMT = "{!s}={!r}"
DEFAULT_SEP = ", "


def str(obj, info=None):
    """This function can be used as a default implementation of __str__() in user-defined classes.
    Classes using this should provide an __info__() method (or directly provide the 'info' part as
    an argument to this function)."""
    if info is None:
        info = obj.__info__()
    return "{}({})".format(type(obj).__name__, info)


def repr(obj, str=None):
    """Default implementation of __repr__() for user-defined classes. Simply uses the object's
    string representation (obj.__str__()) and adds the object's memory address at the end (which
    is often times useful)."""
    if str is None:
        str = obj.__str__()
    return "<{} @{:x}>".format(str, id(obj))


def info(attrs=None, default_fmt=DEFAULT_FMT, default_sep=DEFAULT_SEP):
    """This function is intended to be used as a __info__() method factory, as in
        class foo(object):
            __str__ = pretty.str
            __repr__ = pretty.repr
            __info__ = pretty.info(["x", "y", "z"])

    The returned function builds a string representation of a list of (attr_name, attr_value)
    pairs. Separator and format strings may be specified to customize how the pairs are joined,
    and how each pair is formatted, respectively. If no 'attrs' list is given, it is dynamically
    built based on the object's '__dict__'.

    See also the pretty.klass() class decorator.
    """
    def __info__(obj, fmt=default_fmt, sep=default_sep):
        if attrs is None:
            final_attrs = sorted(obj.__dict__.iterkeys())
        else:
            final_attrs = attrs
        return sep.join(fmt.format(attr, getattr(obj, attr)) for attr in final_attrs)
    return __info__


def klass(cls=None, attrs=None, default_fmt=DEFAULT_FMT, default_sep=DEFAULT_SEP):
    """Sets the defaults for __str__, __repr__ and __info__ on the argument class. This function
    can be used as a class decorator or called as a normal function.

    Both __str__ and __repr__ are set to this module's str() and repr() functions only if the
    corresponding methods are not defined directly in the decorated class. If 'attrs' is not
    supplied, it is assumed that __info__() will be implemented by the class. If 'attrs' is
    given, the __info__ method is defined as pretty.info() using the given attribute list,
    format string, and separator. """
    if cls is None:
        return partial(
            klass,
            attrs=attrs,
            default_fmt=default_fmt,
            default_sep=default_sep
        )
    if "__str__" not in cls.__dict__:
        cls.__str__ = str
    if "__repr__" not in cls.__dict__:
        cls.__repr__ = repr
    if "__info__" not in cls.__dict__ or attrs is not None:
        cls.__info__ = info(attrs, default_fmt, default_sep)
    return cls


def _example():
    @klass
    class foo(object):
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    f = foo(x=234, y=40)
    print "created object f = foo(x=234, y=40)"
    print "f.__info__() -->", f.__info__()
    print "str(f) -->", str(f)
    print "repr(f) -->", repr(f)
    return f
