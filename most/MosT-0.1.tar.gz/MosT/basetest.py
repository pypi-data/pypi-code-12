# -*- coding: utf-8 -*-
__author__ = 'tangke'
import unittest
from functools import wraps
from types import FunctionType

from datacontext import DataContext
from MosT.requestmanager import send_http


def wrap_http(func):
    result = None
    case_list = DataContext.case_list
    for case in case_list:
        if case.casemethod == func.__name__:
            result = send_http(case)

    @wraps(func)
    def _wrap(args):
        func(args, result)

    return _wrap


class BaseTestMeta(type):
    def __new__(cls, name, base, dct):
        for name, value in dct.iteritems():
            if name.startswith('test') and type(value) == FunctionType:
                value = wrap_http(value)
                dct[name] = value
        return type.__new__(cls, name, base, dct)


class BaseTest(unittest.TestCase):
    __metaclass__ = BaseTestMeta

    @classmethod
    def get_case(cls):
        if cls.tests is None:
            cls.logger.error(u'没有case列表，名叫tests')
            import sys
            sys.exit(-1)
        return unittest.TestSuite(map(cls, cls.tests))