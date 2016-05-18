# encoding: utf-8
from __future__ import absolute_import
import unittest

from sd.utils.bean import BaseBean

__author__ = u'Yonka'


def can_not_init(self, v):
    raise AssertionError(u"can not initiate")


class EnumMetaCls(type):
    def __setattr__(cls, key, value):
        if key != u"__init__":
            value.name = key
        super(EnumMetaCls, cls).__setattr__(key, value)

    def __new__(mcs, name, parents, dct):
        if u"_instances" not in dct:
            dct[u"_instances"] = {}
        return super(EnumMetaCls, mcs).__new__(mcs, name, parents, dct)


class CommonNameValueEnum(BaseBean):
    _instances = {}

    def __init__(self, v):
        self.v = v
        self.name = u""
        self.__class__._instances[v] = self

    def get_value(self):
        return self.v

    def from_value(self, v):
        return self.__class__._instances.get(v)

    def __str__(self):
        return u"Enum(%d)" % self.v

    def to_dict(self):
        return self.v
        # return self.name


class TestEnum(unittest.TestCase):
    def test_common_key_value_enum_class(self):
        class TEnum1(CommonNameValueEnum):
            __metaclass__ = EnumMetaCls

            def __str__(self):
                return u"TEnum1(%d)" % self.v

        TEnum1.A = TEnum1(1)
        TEnum1.B = TEnum1(2)
        TEnum1.__init__ = can_not_init

        res = False
        try:
            TEnum1(3)
        except AssertionError:
            res = True
        assert res
        assert TEnum1.A.name == u"A"
        assert len(TEnum1._instances) == 2

        class TEnum2(CommonNameValueEnum):
            __metaclass__ = EnumMetaCls

            def __str__(self):
                return u"TEnum1(%d)" % self.v

        TEnum2.C = TEnum2(1)
        TEnum2.D = TEnum2(2)
        TEnum2.E = TEnum2(3)
        TEnum2.__init__ = can_not_init

        assert len(TEnum2._instances) == 3
        assert len(CommonNameValueEnum._instances) == 0
