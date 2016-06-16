"""Tests for nx_itertools.extra.divide"""
from nx_itertools.extra import divide


def test_normal():
    """Test divide."""
    # 8 / 2
    data = iter('ABCDEFGH')
    res = divide(data, 2)
    assert next(res) == ('A', 'B', 'C', 'D')
    assert list(res) == [('E', 'F', 'G', 'H')]
    assert list(data) == []

    # 8 / 3
    data = iter('ABCDEFGH')
    res = divide(data, 3)
    assert next(res) == ('A', 'B', 'C')
    assert list(res) == [('D', 'E', 'F'), ('G', 'H')]
    assert list(data) == []

    # 7 / 3
    data = iter('ABCDEFG')
    res = divide(data, 3)
    assert next(res) == ('A', 'B', 'C')
    assert list(res) == [('D', 'E'), ('F', 'G')]
    assert list(data) == []

    # 1 / 3
    data = iter('A')
    res = divide(data, 3)
    assert next(res) == ('A',)
    assert list(res) == [(), ()]
    assert list(data) == []

    # 0 / 3
    data = ()
    res = divide(data, 3)
    assert next(res) == ()
    assert list(res) == [(), ()]

    # 3 / 0
    data = iter('ABC')
    res = divide(data, 0)
    assert list(res) == []
    assert list(data) == ['A', 'B', 'C']
