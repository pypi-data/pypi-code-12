# coding: utf-8
"""
    tests.test_core_fieldref
    ~~~~~~~~~~~~~~~~~~~~~~~~
    pyextend.core.fieldref test case

    :copyright: (c) 2016 by Vito.
    :license: GNU, see LICENSE for more details.
"""
import pytest

from pyextend.core.fieldref import NonNegative


def test_nonnegative():

    class Person(object):
        age = NonNegative(1)
        score = NonNegative(0)

        def __init__(self, name, age, score):
            self.name = name
            self.age = age
            self.score = score

    a = Person('jim', 10, 100)
    assert a.age == 10
    assert a.score == 100
    with pytest.raises(ValueError):
        a.age = -1


if __name__ == '__main__':
    pytest.main(__file__)
