# -*- coding: utf-8 -*-
"""Immutable defaults arguments
============================

This module provides facilities for turning mutable default function arguments
into immutable ones. It is fairly lightweight and has no non-standard dependencies.
You can install this package with the standard ``pip`` command::

    $ pip install immutable_default_args

The issue with `mutable argument default values <http://stackoverflow.com/questions/1132941/least-astonishment-in-python-the-mutable-default-argument>`_ is pretty well known in Python.
Basically mutable default values are assigned once at define time and can then
be modified within the function body which might come as a surprise.
Here is the example from the `stackoverfow <http://stackoverflow.com/questions/1132941/least-astonishment-in-python-the-mutable-default-argument>`_ thread::

    def foo(a=[]):
        a.append(5)
        return a

    >>> foo()
    [5]
    >>> foo()
    [5, 5]
    >>> foo()
    [5, 5, 5]
    ...

The default way of preventing this behaviour is to use ``None`` as the default
and check for it in the function body, like so::

    def foo(a=None):
        a = a if (type(a) is list) else []
        a.append(5)
        return a

    >>> foo()
    [5]
    >>> foo()
    [5]
    ...

Usage
-----

This package aims to offer two additional options to fix this issue:

* With a handy function decorator ``@fix_mutable_kwargs`` to fix a certain function.
* With a metaclass ``ImmutableDefaultArguments`` to fix all *methods*, *classmethods* and *staticmethods* at once.

Using the decorator::

    from immutable_default_args import fix_mutable_kwargs

    @fix_mutable_kwargs
    def foo(a=[]):
        a.append(5)
        return a

    >>> foo()
    [5]
    >>> foo()
    [5]
    ...

It doesn't matter if the iterable is empty or not::

    @fix_mutable_kwargs
    def foo(a=[1, 2, {'key': 'value'}, 3, 4]):
        a.append(5)
        return a

    >>> foo()
    [1, 2, {'key': 'value'}, 3, 4, 5]
    >>> foo()
    [1, 2, {'key': 'value'}, 3, 4, 5]
    ...

Fixing all mutable default values for all methods of an object via the ``ImmutableDefaultArguments`` metaclass::

    class Foo(object):

        __metaclass__ = ImmutableDefaultArguments  # Py2 syntax

        def foo(self, a=[]):
            a.append(5)
            return a

        @classmethod  # staticmethods work as well
        def foo_classmethod(cls, a=[]):
            a.append(5)
            return a

    instance_of_foo = Foo()
    >>> instance_of_foo.foo()
    [5]
    >>> instance_of_foo.foo()
    [5]
    ...
    >>> Foo.foo_classmethod()
    [5]
    >>> Foo.foo_classmethod()
    [5]

Compatibility
-------------

The ``immutable_default_args`` is tested against Py2/3 and should and is supported from *Py2.7* upstream.

History
-------

0.0.3
*****
* Date: 08.05.2016
* Features/Changes: Fixed documentation

0.0.2
*****
* Date: 08.05.2016
* Features/Changes:
    * Added ``@fix_mutable_kwargs`` decorator
    * Refactorings/Cleanup

0.0.1
*****
* Date: 01.05.2016
* Features/Changes: First release. Included only ``ImmutableDefaultArguments`` metaclass

License
-------

You are free to do whatever you like with the code. However I am not accountable for anything....ever.
"""


__all__ = ['fix_mutable_kwargs', 'ImmutableDefaultArguments',]


import sys
import logging
from array import array
from itertools import islice
from functools import wraps
from inspect import(
    getargspec,
    isfunction,
    ismethod
)
from collections import(
    MutableMapping,
    MutableSequence,
    MutableSet,
    OrderedDict
)


IS_PYTHON3 = sys.version_info >= (3, 0)
IS_PYTHON2 = not IS_PYTHON3


MUTABLE_TYPES = (MutableMapping, MutableSequence, MutableSet, array)


# modify for python 2
if(IS_PYTHON2 is True):
    mutables_types_python_2 = (bytearray,)
    MUTABLE_TYPES = MUTABLE_TYPES + mutables_types_python_2


# modify for python 3
elif(IS_PYTHON3 is True):
    pass


logger = logging.getLogger(__name__)


def mutable_to_immutable_kwargs(names_to_defaults, pos_arg_names):
    """The actual logic responsible for replacing mutable kwargs on a function
    call.
    """
    def closure(func):
        @wraps(func)
        def wrapped_func(*args, **kwargs):

            # number of kwargs specified positionally
            start = len(args) - len(pos_arg_names)

            # exclude explicitly specified kwargs
            set_kwarg_names = set(kwargs)
            set_registered_kwarg_names = set(islice(names_to_defaults, start, None))
            defaults_to_replace = set_registered_kwarg_names - set_kwarg_names

            for name in defaults_to_replace:
                define_time_object = names_to_defaults[name]

                # special handling for types
                if(isinstance(define_time_object, (array, ))):
                    typecode = define_time_object.typecode
                    items = define_time_object.tolist()
                    kwargs[name] = type(define_time_object)(typecode, items)

                # default handling
                else:
                    kwargs[name] = type(define_time_object)(define_time_object)

            return func(*args, **kwargs)
        return wrapped_func
    return closure


def function_to_kwarg_fixed_function(func):
    """Introspect given function and return kwarg fixed function if applicable.
    """

    # account for class/staticmethods
    class_or_static_method = None
    if (isinstance(func, (classmethod, staticmethod))):
        class_or_static_method = type(func)
        function_object = getattr(func, '__func__')
    else:
        function_object = func

    # introspect function
    arg_specs = getargspec(function_object)
    arg_names = arg_specs.args
    arg_defaults = arg_specs.defaults

    # function contains names and defaults?
    if (None in (arg_names, arg_defaults)):
        return function_object

    # exclude self, cls and pos. args.
    names_to_defaults = list(zip(reversed(arg_defaults),
                                 reversed(arg_names)))
    names_to_defaults = list(reversed(names_to_defaults))
    names_to_defaults = [(arg_name, arg_default) for
                         arg_default, arg_name in
                         names_to_defaults]

    # sort out mutable defaults and their arg. names
    mutable_names_to_defaults = OrderedDict()
    for arg_name, arg_default in names_to_defaults:
        if (isinstance(arg_default, MUTABLE_TYPES)):
            mutable_names_to_defaults.setdefault(arg_name, arg_default)

    # did we have any args with mutable defaults ?
    if not mutable_names_to_defaults:
        return function_object

    # account for the fact that we can fill values for default args.
    # with positional args.
    pos_arg_names = arg_names[:-len(arg_defaults)]

    # replace original function with decorated function
    closure = mutable_to_immutable_kwargs(
        mutable_names_to_defaults, pos_arg_names)
    kwarg_fixed_function = closure(function_object)

    # return
    if (class_or_static_method is not None):
        return class_or_static_method(kwarg_fixed_function)

    return kwarg_fixed_function


def fix_mutable_kwargs(func):
    """Decorate functions to *fix* mutable kwargs by re-instanciating
    registered default argument values on each function call.
    """

    return function_to_kwarg_fixed_function(func)


class ImmutableDefaultArguments(type):
    """Search through the attrs. dict for functions with mutable default args.
    and replace matching attr. names with a function object that fixes mutable
    kwargs.
    """

    def __new__(meta, name, bases, attrs):

        for obj_name, obj in list(attrs.items()):

            # is it a compatible type ?
            if (isfunction(obj) is False
                and ismethod(obj) is False
                and type(obj) is not classmethod
                and type(obj) is not staticmethod):

                continue

            # create and assign wrapped function object
            func_name, func_obj = obj_name, obj
            attrs[func_name] = function_to_kwarg_fixed_function(func_obj)

        metaclass = super(ImmutableDefaultArguments, meta)
        return metaclass.__new__(meta, name, bases, attrs)
