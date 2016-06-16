"""Tests for nx_itertools.extra.split"""
from nx_itertools.extra import split


def test_normal():
    """Test split."""
    # split on A, trailing
    data = iter('BCAADEAFG')
    res = split(lambda x: x == 'A', data)
    assert next(res) == ['B', 'C', 'A']
    assert list(res) == [['A'],
                         ['D', 'E', 'A'],
                         ['F', 'G']]
    assert list(data) == []

    # split on A, trailing - note A is at start and end of data
    data = iter('ABCAADEAFGAA')
    res = split(lambda x: x == 'A', data)
    assert next(res) == ['A']
    assert list(res) == [['B', 'C', 'A'],
                         ['A'],
                         ['D', 'E', 'A'],
                         ['F', 'G', 'A'],
                         ['A']]
    assert list(data) == []

    # split on A, trailing - A not in data
    data = iter('BCD')
    res = split(lambda x: x == 'A', data)
    assert list(res) == [['B', 'C', 'D']]
    assert list(data) == []

    # split on A, trailing - empty
    data = ()
    res = split(lambda x: x == 'A', data)
    assert list(res) == []

    # split on A, leading
    data = iter('BCAADEAFG')
    res = split(lambda x: x == 'A', data, trailing=False)
    assert next(res) == ['B', 'C']
    assert list(res) == [['A'],
                         ['A', 'D', 'E'],
                         ['A', 'F', 'G']]
    assert list(data) == []

    # split on A, leading - note A is at start and end of data
    data = iter('ABCAADEAFGA')
    res = split(lambda x: x == 'A', data, trailing=False)
    assert next(res) == ['A', 'B', 'C']
    assert list(res) == [['A'],
                         ['A', 'D', 'E'],
                         ['A', 'F', 'G'],
                         ['A']]
    assert list(data) == []

    # split on A, leading - A not in data
    data = iter('BCD')
    res = split(lambda x: x == 'A', data, trailing=False)
    assert next(res) == ['B', 'C', 'D']
    assert list(res) == []
    assert list(data) == []

    # split on A, leading - empty
    data = ()
    res = split(lambda x: x == 'A', data, trailing=False)
    assert list(res) == []
