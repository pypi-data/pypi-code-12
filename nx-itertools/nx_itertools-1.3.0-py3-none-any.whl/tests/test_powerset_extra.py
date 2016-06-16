"""Test for nx_itertools.extra.powerset"""
from nx_itertools import extra


def test_normal():
    """Test powerset."""
    # powerset forward
    data = iter('ABC')
    res = extra.powerset(data)
    assert next(res) == ()
    assert list(res) == [('A',), ('B',), ('C',), ('A', 'B'), ('A', 'C'),
                         ('B', 'C'), ('A', 'B', 'C')]
    assert list(data) == []

    # extra.powerset reverse
    data = iter('ABC')
    res = extra.powerset(data, reverse=True)
    assert next(res) == ('A', 'B', 'C')
    assert list(res) == [('A', 'B'), ('A', 'C'), ('B', 'C'), ('A',), ('B',),
                         ('C',), ()]
    assert list(data) == []

    # extra.powerset empty, forward
    data = ()
    res = extra.powerset(data)
    assert list(res) == [()]

    # extra.powerset empty, reverse
    data = ()
    res = extra.powerset(data, reverse=True)
    assert list(res) == [()]
