# encoding: utf-8
import unittest

__author__ = 'Yonka'


class _ListGenericMeta(type):
    def __getitem__(cls, item):
        class _List(List):
            __parameters__ = (item,)

        return _List


class List(list):
    __metaclass__ = _ListGenericMeta


class TestTyping(unittest.TestCase):
    def test_list(self):
        t = List[int]
        assert "__parameters__" in t.__dict__
