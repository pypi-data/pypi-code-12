"""Test for nx_itertools.recipes.partition"""
from nx_itertools import recipes


def test_normal():
    """Test partition."""
    # partition with positive and negative
    data = iter('ABCDEF')
    res = recipes.partition(lambda x: x in 'ACEG', data)
    assert list(res[0]) == ['B', 'D', 'F']
    assert list(res[1]) == ['A', 'C', 'E']
    assert list(data) == []

    # partition with only positive
    data = iter('ACE')
    res = recipes.partition(lambda x: x in 'ACEG', data)
    assert list(res[0]) == []
    assert list(res[1]) == ['A', 'C', 'E']
    assert list(data) == []

    # partition with only negative
    data = iter('BDF')
    res = recipes.partition(lambda x: x in 'ACEG', data)
    assert list(res[0]) == ['B', 'D', 'F']
    assert list(res[1]) == []
    assert list(data) == []

    # partition empty
    data = ()
    res = recipes.partition(lambda x: x in 'ACEG', data)
    assert list(res[0]) == []
    assert list(res[1]) == []
