"""Test for nx_itertools.extra.pairwise"""
from nx_itertools import extra


def test_normal():
    """Test pairwise."""
    # extra.pairwise with more than one element
    data = iter('ABCD')
    res = extra.pairwise(data)
    assert next(res) == ('A', 'B')
    assert list(res) == [('B', 'C'), ('C', 'D')]
    assert list(data) == []

    # extra.pairwise with one element
    data = iter('A')
    res = extra.pairwise(data)
    assert list(res) == []
    assert list(data) == []

    # extra.pairwise with empty
    data = ()
    res = extra.pairwise(data)
    assert list(res) == []


def test_normal_peek():
    """Test pairwise with peeking at iterable."""
    # extra.pairwise with more than one element
    data = iter('ABCD')
    res = extra.pairwise(data)
    assert next(res) == ('A', 'B')
    assert next(data) == 'C'
    assert list(res) == [('B', 'D')]    # C removed so B is paired with D
    assert list(data) == []


