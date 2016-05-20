# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Description
__author__ = "Jorge A. Medina"
from inspect import getmembers, isclass


def factorize(module=None, object_type=None, *args, **kwargs):
    """ Object instance factory instances type from module
    both passed as argument of the function support positional
    and key words arguments module and type
    :param type: dict module='name'
    :param type: dict object_type='nane'
    :param type: list
    :param type: dict
    :return: type: object
    """
    if not module or not object_type:
        raise ArgumentError()
    try:
        imported_mod = __import__(module)
    except ImportError:
        raise NonExistentModuleError(module)

    for name, obj in getmembers(imported_mod):
        if isclass(obj) and name == object_type:
            return obj(*args, **kwargs)
    raise NonExistentTypeError(object_type)


class ArgumentError(ValueError):
    """ ArgumentError raises if not receive correct arguments or miss them.
    """
    def __init__(self):
        msg = "Error: missing values in call of factorize"
        super().__init__(msg)


class NonExistentTypeError(NotImplementedError):
    """ NonExistentTypeError Exception raises when type
    there not implemented
    """
    def __init__(self, *args, **kwargs):
        msg = "Error: can't factorize the object type {}".format(args)
        super().__init__(msg)


class NonExistentModuleError(ImportError):
    """ NonExistentModuleError This exception raises when module
    can't be achieved maybe not exist or are not in the class path
    """
    def __init__(self, *args, **kwargs):
        msg = "Error: can't load the module {}".format(args)
        super().__init__(msg)
