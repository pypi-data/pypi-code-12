"""Test for nx_itertools.recipes.ncycles"""
from nx_itertools.recipes import ncycles


def test_normal():
    """Test ncycles."""
    # ncycle 3 times
    data = iter('ABC')
    res = ncycles(data, 3)
    assert next(res) == 'A'
    assert list(res) == ['B', 'C', 'A', 'B', 'C', 'A', 'B', 'C']
    assert list(data) == []

    # ncycle 3 times, no data
    data = ()
    res = ncycles(data, 3)
    assert list(res) == []

    # ncycle 0 times
    data = iter('ABC')
    res = ncycles(data, 0)
    assert list(res) == []
    assert list(data) == []

    # ncycle 0 times, no data
    data = ()
    res = ncycles(data, 0)
    assert list(res) == []
