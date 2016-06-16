#!/usr/bin/env python
import builtins
import inspect
# from cyfunction import *
from formatfunction import formatfunction
import formatvalue
from objectname import objectname
from public import public
from issharedobject import issharedobject


def issystem(cls):
    return hasattr(builtins, cls.__name__)


def defargs(obj):
    argspec = inspect.getargspec(obj)
    return argspec.args


def formatbases(cls, fullname=True):
    __bases__ = cls.__bases__
    if not __bases__:
        return ""
    clsnames = []
    for base in __bases__:
        module = inspect.getmodule(base)
        if cls.__module__ == module:
            clsnames.append(base.__name__)
        else:
            name = objectname(base, fullname=fullname)
            clsnames.append(name)
    return "(%s)" % ",".join(clsnames)


@public
def formatclass(cls, fullname=True, args=True,
                formatvalue=formatvalue.formatvalue):
    """todo"""
    name = cls.__name__ + formatbases(cls, fullname=fullname)
    # args = False # by default no
    if not issharedobject(cls) and hasattr(cls, "__init__"):
        # if iscyfunction(cls.__init__):
            # args = False
        # else:
        if inspect.ismethoddescriptor(cls.__init__):
            args = False
        else:  # python source
            if len(defargs(cls.__init__)) == 1:
                args = False
    if not args:
        return name
    return name + formatfunction(cls.__init__,
                                 name=False,
                                 formatvalue=formatvalue,
                                 firstarg=False
                                 )
