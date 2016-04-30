# coding: utf-8
"""
    tests.test_core_wrappers_singleton
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    pyextend.core.wrappers.singleton test case

    :copyright: (c) 2016 by Vito.
    :license: GNU, see LICENSE for more details.
"""
import pytest

from pyextend.core.wrappers.singleton import singleton


def test_singleton():
    @singleton
    class SObj(object):
        pass

    obj1 = SObj()
    obj2 = SObj()
    assert id(obj1) == id(obj2)
    assert obj1 == obj2
    obj1.A = 1
    assert obj2.A == 1

if __name__ == '__main__':
    pytest.main(__file__)
