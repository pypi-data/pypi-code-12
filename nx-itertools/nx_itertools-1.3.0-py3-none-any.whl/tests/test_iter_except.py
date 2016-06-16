"""Test for nx_itertools.recipes.iter_except"""
from itertools import repeat
from nx_itertools.recipes import iter_except


class Ex(Exception):
    """Custom exception for which to test."""
    pass


def func(idx):
    """Identity function that raises Ex when called with 3."""
    if idx == 3:
        raise Ex
    return idx


def test_normal():
    """Test iter_except."""
    # exception triggered
    gen = (func(x) for x in range(10))
    res = iter_except(lambda: next(gen), Ex)
    assert next(res) == 0
    assert list(res) == [1, 2]

    # no exception
    gen = (func(x) for x in repeat(3))
    res = iter_except(lambda: next(gen), Ex)
    assert list(res) == []

    # exception triggered with first
    gen = (func(x) for x in range(10))
    res = iter_except(lambda: next(gen), Ex, lambda: 'A')
    assert next(res) == 'A'
    assert list(res) == [0, 1, 2]

    # exception triggered on first
    gen = (func(x) for x in range(10))
    res = iter_except(lambda: next(gen), Ex, lambda: func(3))
    assert list(res) == []
