"""Test for nx_itertools.recipes.repeatfunc"""
from itertools import islice
from nx_itertools.recipes import repeatfunc


def func(*args):
    """Function that returns the provided tuple with 'A' prepended."""
    return ('A',) + args


def test_no_args():
    """Test repeatfunc."""
    # repeat forever with no args
    res = repeatfunc(func)
    assert next(res) == ('A',)
    assert list(islice(res, 2)) == [('A',), ('A',)]

    # repeat forever with no args
    res = repeatfunc(func, None)
    assert next(res) == ('A',)
    assert list(islice(res, 2)) == [('A',), ('A',)]

    # repeat forever with args
    res = repeatfunc(func, None, 'X', 'Y')
    assert next(res) == ('A', 'X', 'Y')
    assert list(islice(res, 2)) == [('A', 'X', 'Y'), ('A', 'X', 'Y')]

    # repeat twice with no args
    res = repeatfunc(func, 2)
    assert next(res) == ('A',)
    assert list(res) == [('A',)]

    # repeat twice with args
    res = repeatfunc(func, 2, 'X', 'Y')
    assert next(res) == ('A', 'X', 'Y')
    assert list(res) == [('A', 'X', 'Y')]
