"""Test for nx_itertools.recipes.powerset"""
from nx_itertools import recipes


def test_normal():
    """Test powerset."""
    data = iter('ABC')
    res = recipes.powerset(data)
    assert next(res) == ()
    assert list(res) == [('A',), ('B',), ('C',), ('A', 'B'), ('A', 'C'),
                         ('B', 'C'), ('A', 'B', 'C')]
    assert list(data) == []

    data = ()
    res = recipes.powerset(data)
    assert list(res) == [()]
