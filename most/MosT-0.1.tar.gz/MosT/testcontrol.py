# -*- coding: utf-8 -*-
__author__ = 'tangke'
import unittest
import sys

from datacontext import DataContext
from universalconfig import read_database_config, read_request_obj, read_global_config
from log import MyLog
from MosT.basetest import BaseTest


def _init_config():
    _init_env()
    read_database_config()
    read_request_obj()
    read_global_config()


def _init_env():
    if len(sys.argv) > 1:
        DataContext.env = sys.argv[1]
    else:
        DataContext.env = 'test'
    MyLog.log().debug('本次测试的环境是:' + DataContext.env)


def _get_suites(cls_name_list):
    suites_list = []
    for cls in cls_name_list:
        try:
            class_ = __import__(cls)
        except ImportError, e:
            raise e
        for name in dir(class_):
            obj = getattr(class_, name)
            if isinstance(obj, type) and issubclass(obj, unittest.TestCase) and obj is not BaseTest:
                suites_list.append(obj)
    return [cls_name.get_case() for cls_name in suites_list]


def _run(case_list):
    runner = unittest.TextTestRunner()
    suite = unittest.TestSuite(_get_suites(case_list))
    runner.run(suite)


def control(*args):
    _init_config()
    _run(args)
