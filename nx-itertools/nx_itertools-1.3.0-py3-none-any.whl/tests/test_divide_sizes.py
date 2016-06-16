"""Tests for nx_itertools.extra.divide_sizes"""
from nx_itertools.extra import divide_sizes


def test_normal():
    """Test divide_sizes."""
    # 8 / 2
    res = divide_sizes(8, 2)
    assert res == [4, 4]

    # 8 / 3
    res = divide_sizes(8, 3)
    assert res == [3, 3, 2]

    # 7 / 3
    res = divide_sizes(7, 3)
    assert res == [3, 2, 2]

    # 1 / 3
    res = divide_sizes(1, 3)
    assert res == [1, 0, 0]

    # 0 / 3
    res = divide_sizes(0, 3)
    assert res == [0, 0, 0]

    # 3 / 0
    res = divide_sizes(3, 0)
    assert res == []


def test_oddity():
    """Test oddities of divide_sizes."""
    # count is negative but 3 buckets requested
    res = divide_sizes(-3, 3)
    assert res == [0, 0, 0]

    # count is negative but no buckets requested
    res = divide_sizes(-3, 0)
    assert res == []
