# -*- coding: utf-8 -*-
__all__ = ['ImmutableDefaultArguments',]

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
    MutableSet
)

from immutable_default_args.compatibility import OrderedDict


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
    """Decorator to return function that replaces default values for registered
    names with a new instance of default value.
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


class ImmutableDefaultArguments(type):
    """Search through the attrs. dict for functions with mutable default args.
    and replace matching attr. names with a function object from the above
    decorator.
    """

    def __new__(meta, name, bases, attrs):

        for obj_name, obj in list(attrs.items()):

            # is it a compatible type ?
            if(isfunction(obj) is False and
               ismethod(obj) is False and
               type(obj) is not classmethod and
               type(obj) is not staticmethod):
                continue

            # account for classmethods
            if(isinstance(obj, (classmethod, staticmethod))):
                function_object = getattr(obj, '__func__')
            else:
                function_object = obj

            function_name = obj_name

            arg_specs = getargspec(function_object)
            arg_names = arg_specs.args
            arg_defaults = arg_specs.defaults

            # function contains names and defaults?
            if (None in (arg_names, arg_defaults)):
                continue

            # exclude self and pos. args.
            names_to_defaults = list(zip(reversed(arg_defaults),
                                         reversed(arg_names)))
            names_to_defaults = list(reversed(names_to_defaults))
            names_to_defaults = [(arg_name, arg_default) for
                                 arg_default, arg_name in
                                 names_to_defaults]

            # sort out mutable defaults and their arg. names
            mutable_names_to_defaults = OrderedDict()
            for arg_name, arg_default in names_to_defaults:
                if(isinstance(arg_default, MUTABLE_TYPES)):
                    mutable_names_to_defaults.setdefault(arg_name, arg_default)

            # did we have any args with mutable defaults ?
            if not mutable_names_to_defaults:
                continue

            # account for the fact that we can fill values for default args.
            # with positional args.
            pos_arg_names = arg_names[:-len(arg_defaults)]

            # replace original function with decorated function
            closure = mutable_to_immutable_kwargs(
                mutable_names_to_defaults, pos_arg_names)
            function = closure(function_object)

            # assign
            if (type(obj) is classmethod):
                attrs[function_name] = classmethod(function)
            elif (type(obj) is staticmethod):
                attrs[function_name] = staticmethod(function)
            else:
                attrs[function_name] = function

        return super(ImmutableDefaultArguments, meta).__new__(meta, name, bases, attrs)
