"""Test for nx_itertools.recipes.pairwise"""
from nx_itertools import recipes


def test_normal():
    """Test pairwise."""
    # recipes.pairwise with more than one element
    data = iter('ABCD')
    res = recipes.pairwise(data)
    assert next(res) == ('A', 'B')
    assert list(res) == [('B', 'C'), ('C', 'D')]
    assert list(data) == []

    # recipes.pairwise with one element
    data = iter('A')
    res = recipes.pairwise(data)
    assert list(res) == []
    assert list(data) == []

    # recipes.pairwise with empty
    data = ()
    res = recipes.pairwise(data)
    assert list(res) == []


def test_normal_peek():
    """Test pairwise with peeking at iterable."""
    # recipes.pairwise with more than one element
    data = iter('ABCD')
    res = recipes.pairwise(data)
    assert next(res) == ('A', 'B')
    assert next(data) == 'C'
    assert list(res) == [('B', 'D')]    # C removed so B is paired with D
    assert list(data) == []


