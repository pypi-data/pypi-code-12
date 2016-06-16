"""Test for nx_itertools.recipes.tabulate"""
from itertools import islice
from nx_itertools.recipes import tabulate


def test_normal():
    """Test tabulate."""
    # tabulate with default: 0
    res = tabulate(lambda x: 'A' + str(x))
    assert next(res) == 'A0'
    assert list(islice(res, 4)) == ['A1', 'A2', 'A3', 'A4']

    # tabulate with start of -2
    res = tabulate(lambda x: 'A' + str(x), -2)
    assert next(res) == 'A-2'
    assert list(islice(res, 4)) == ['A-1', 'A0', 'A1', 'A2']
