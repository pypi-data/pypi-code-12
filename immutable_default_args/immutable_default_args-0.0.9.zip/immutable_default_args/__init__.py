# -*- coding: utf-8 -*-
"""Very small package to automatically safeguard mutable function arguments,
preventing them from being modified.
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
