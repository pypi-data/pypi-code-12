"""Test for nx_itertools.extra.partition"""
from nx_itertools import extra


def test_normal():
    """Test partition."""
    # partition with positive and negative
    data = iter('ABCDEF')
    res = extra.partition(lambda x: x in 'ACEG', data)
    assert res == (['B', 'D', 'F'], ['A', 'C', 'E'])
    assert list(data) == []

    # partition with only positive
    data = iter('ACE')
    res = extra.partition(lambda x: x in 'ACEG', data)
    assert res == ([], ['A', 'C', 'E'])
    assert list(data) == []

    # partition with only negative
    data = iter('BDF')
    res = extra.partition(lambda x: x in 'ACEG', data)
    assert res == (['B', 'D', 'F'], [])
    assert list(data) == []

    # partition empty
    data = ()
    res = extra.partition(lambda x: x in 'ACEG', data)
    assert res == ([], [])
