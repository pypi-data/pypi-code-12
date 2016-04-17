# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

import pytest

from restdef.utils.decorators import (
    init_parameters,
    list_d,
    tuple_d,
)


def test_on_init():

    class Case(object):

        @init_parameters([
            ('a', int),
            ('b', list),
            ('c', list, [1, 2, 3]),
        ])
        def __init__(self):
            assert self.a == 42
            assert self.b
            assert self.c == [1, 2, 3]

    Case(42, [1])
    with pytest.raises(AssertionError):
        Case(42, [])
    with pytest.raises(AssertionError):
        Case(42, [1], [1, 2, 3, 4])
    Case(42, [1], [1, 2, 3])

    with pytest.raises(TypeError):
        Case(1.0)
    with pytest.raises(TypeError):
        Case(42, 1)
    with pytest.raises(TypeError):
        Case(42, [1, 2, 3], 42)


def test_none():

    class Case(object):

        parameters = [
            ('a', int, None),
            ('b', list, None),
        ]

        @init_parameters(parameters)
        def __init__(self):
            pass

    Case()
    Case(1)
    Case(1, [])
    Case(None)
    Case(None, None)


def test_on_typeobj():

    @init_parameters([
        ('a', int),
    ])
    class Case1(object):
        pass

    Case1(1)
    with pytest.raises(TypeError):
        Case1(1.0)

    @init_parameters([
        ('a', int),
    ])
    class Case2(object):

        def __init__(self):
            assert self.a != 42

    Case2(1)
    Case2(a=1)
    with pytest.raises(AssertionError):
        Case2(42)


def test_class_parameter():

    @init_parameters
    class Case1(object):

        PARAMETERS = [
            ('a', int),
        ]

    Case1(1)
    Case1(a=1)
    with pytest.raises(TypeError):
        Case1(b=1)

    @init_parameters
    class Case2(object):

        PARAMETERS = [
            ('a', int),
        ]

        def __init__(self):
            assert self.a != 42

    Case2(1)
    Case2(a=1)
    with pytest.raises(AssertionError):
        Case2(42)


def test_nested_type():

    @init_parameters
    class Case(object):

        PARAMETERS = [
            ('a', [list, tuple]),
        ]

    Case(
        [1, 2],
    )
    Case(
        (1, 2),
    )
    with pytest.raises(TypeError):
        Case(1)

    with pytest.raises(TypeError):

        @init_parameters
        class Case1(object):

            PARAMETERS = [
                ('a', [list, 1]),
            ]


def test_none_2():

    @init_parameters
    class Case1(object):

        PARAMETERS = [
            ('a', int, None),
        ]

    @init_parameters
    class Case2(object):

        PARAMETERS = [
            ('a', type(None)),
        ]

    @init_parameters
    class Case3(object):

        PARAMETERS = [
            ('a', int),
        ]

    Case1()
    Case1(None)
    Case2(None)
    with pytest.raises(TypeError):
        Case3(None)


def test_corner_case():

    with pytest.raises(TypeError):
        init_parameters([])(1)

    with pytest.raises(TypeError):

        @init_parameters([
            ('name',),
        ])
        class Case1(object):
            pass

    with pytest.raises(SyntaxError):

        @init_parameters([
            ('duplicates', bool),
            ('duplicates', bool),
        ])
        class Case2(object):
            pass

    @init_parameters([
        ('a', int),
    ])
    class Case3(object):
        pass

    with pytest.raises(TypeError):
        Case3()
    with pytest.raises(TypeError):
        Case3(1, 2)
    with pytest.raises(TypeError):
        Case3(1, a=2)
    with pytest.raises(TypeError):
        Case3(b=2)

    with pytest.raises(TypeError):

        @init_parameters([
            ('a', 1),
        ])
        class Case4(object):
            pass


def test_nested_decl():

    @init_parameters
    class Case1(object):

        PARAMETERS = [
            ('a', list_d(int)),
        ]

    Case1(
        [1, 2, 3],
    )
    with pytest.raises(TypeError):
        Case1(
            [1, 2.0],
        )
    with pytest.raises(TypeError):
        Case1(
            (1, 2),
        )

    @init_parameters
    class Case2(object):

        PARAMETERS = [
            ('a', tuple_d(int)),
        ]

    Case2(
        (1, 2, 3),
    )
    with pytest.raises(TypeError):
        Case2(
            (1, 2.0),
        )
    with pytest.raises(TypeError):
        Case2(
            [1, 2],
        )

    @init_parameters
    class Case3(object):

        PARAMETERS = [
            ('a', [list_d(int), tuple_d(int)], None),
            ('b', list_d([int, float]), None),
        ]

    Case3(
        a=[1, 2, 3],
    )
    Case3(
        a=(1, 2, 3),
    )
    Case3(
        b=[1, 2],
    )
    Case3(
        b=[1, 2.0],
    )
    with pytest.raises(TypeError):
        Case3(
            a=[1, 2.0],
        )
    with pytest.raises(TypeError):
        Case3(
            b=(1, 2.0),
        )
