"""Test for nx_itertools.recipes.flatten"""
from nx_itertools.recipes import flatten


def test_normal():
    """Test flatten."""
    # flatten two iterables
    data1, data2 = iter('ABC'), iter('DEF')
    lst = (x for x in (data1, data2))
    res = flatten(lst)
    assert next(res) == 'A'
    assert list(res) == ['B', 'C', 'D', 'E', 'F']
    assert list(lst) == []
    assert list(data1) == []
    assert list(data2) == []

    # flatten one iterable
    data = iter('ABC')
    lst = (x for x in (data,))
    res = flatten(lst)
    assert next(res) == 'A'
    assert list(res) == ['B', 'C']
    assert list(lst) == []
    assert list(data) == []

    # flatten two iterables, one empty
    data1, data2 = iter('ABC'), ()
    lst = (x for x in (data1, data2))
    res = flatten(lst)
    assert next(res) == 'A'
    assert list(res) == ['B', 'C']
    assert list(lst) == []
    assert list(data1) == []

    # flatten two iterables, one empty
    data1, data2 = (), iter('DEF')
    lst = (x for x in (data1, data2))
    res = flatten(lst)
    assert next(res) == 'D'
    assert list(res) == ['E', 'F']
    assert list(lst) == []
    assert list(data2) == []

    # flatten two iterables, both empty
    data1, data2 = (), ()
    lst = (x for x in (data1, data2))
    res = flatten(lst)
    assert list(res) == []
    assert list(lst) == []

    # flatten one iterable, empty
    data = ()
    lst = (x for x in (data,))
    res = flatten(lst)
    assert list(res) == []
    assert list(lst) == []


def test_normal_peek():
    """Test flatten with peeking at iterable."""
    # flatten two iterables
    data1, data2 = iter('ABC'), iter('DEF')
    lst = (x for x in (data1, data2))
    res = flatten(lst)
    assert next(res) == 'A'
    assert next(data1)
    assert list(res) == ['C', 'D', 'E', 'F']
    assert list(lst) == []
    assert list(data1) == []
    assert list(data2) == []

    # flatten one iterable
    data = iter('ABC')
    lst = (x for x in (data,))
    res = flatten(lst)
    assert next(res) == 'A'
    assert next(data) == 'B'
    assert list(res) == ['C']
    assert list(lst) == []
    assert list(data) == []

    # flatten two iterables, one empty
    data1, data2 = iter('ABC'), ()
    lst = (x for x in (data1, data2))
    res = flatten(lst)
    assert next(res) == 'A'
    assert next(data1) == 'B'
    assert list(res) == ['C']
    assert list(lst) == []
    assert list(data1) == []

    # flatten two iterables, one empty
    data1, data2 = (), iter('DEF')
    lst = (x for x in (data1, data2))
    res = flatten(lst)
    assert next(res) == 'D'
    assert next(data2) == 'E'
    assert list(res) == ['F']
    assert list(lst) == []
    assert list(data2) == []
