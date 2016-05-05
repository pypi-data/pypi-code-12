# coding:utf-8
# Copyright (C) Alibaba Group

"""
Errors : A collection of exceptions used in the whole checking process.
"""
from . import __version__

__author__ = "Thomas Li <yanliang.lyl@alibaba-inc.com>"
__license__ = "GNU License"


class Ignore(Exception):
    """This exception can be used as a method return, which could be caught by
    the decorator, after this exception is caught, the decorator should return
    directly.

    """


class Fine(Exception):
    """This Exception used in a check point marked as 'OK'
    """


class Failed(Exception):
    """This Exception used in a check point marked as 'FAILED'
    """
