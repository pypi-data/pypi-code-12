"""Test for nx_itertools.recipes.roundrobin"""
from itertools import islice
from nx_itertools.recipes import roundrobin


def test_normal():
    """Test roundrobin."""
    # three tuples of different sizes
    data1, data2, data3 = iter('ABC'), iter('D'), iter('EF')
    res = roundrobin(data1, data2, data3)
    assert next(res) == 'A'
    assert list(res) == ['D', 'E', 'B', 'F', 'C']
    assert list(data1) == []
    assert list(data2) == []
    assert list(data3) == []

    # three tuples of different sizes in ascending order
    data1, data2, data3 = iter('A'), iter('BC'), iter('DEF')
    res = roundrobin(data1, data2, data3)
    assert next(res) == 'A'
    assert list(res) == ['B', 'D', 'C', 'E', 'F']
    assert list(data1) == []
    assert list(data2) == []
    assert list(data3) == []

    # one tuple
    data = iter('ABC')
    res = roundrobin(data)
    assert next(res) == 'A'
    assert list(res) == ['B', 'C']
    assert list(data) == []

    # empty tuple
    data = ()
    res = roundrobin(data)
    assert list(res) == []

    # nothing
    res = roundrobin()
    assert list(res) == []


def test_normal_peek():
    """Test roundrobin with peeking at iterable."""
    # three tuples of different sizes
    data1, data2, data3 = iter('ABC'), iter('DE'), iter('FG')
    res = roundrobin(data1, data2, data3)
    assert list(islice(res, 3)) == ['A', 'D', 'F']
    assert next(data1) == 'B'
    assert list(res) == ['C', 'E', 'G']
    assert list(data1) == []
    assert list(data2) == []
    assert list(data3) == []

    # three tuples of different sizes in ascending order
    data1, data2, data3 = iter('A'), iter('BC'), iter('DEF')
    res = roundrobin(data1, data2, data3)
    assert next(res) == 'A'
    assert next(data2) == 'B'
    assert list(res) == ['C', 'D', 'E', 'F']
    assert list(data1) == []
    assert list(data2) == []
    assert list(data3) == []

    # one tuple
    data = iter('ABC')
    res = roundrobin(data)
    assert next(res) == 'A'
    assert next(data) == 'B'
    assert list(res) == ['C']
    assert list(data) == []
