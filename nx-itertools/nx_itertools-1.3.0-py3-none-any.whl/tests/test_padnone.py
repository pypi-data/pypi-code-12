"""Test for nx_itertools.recipes.padnone"""
from itertools import islice
from nx_itertools.recipes import padnone


def test_normal():
    """Test padnone."""
    # padnone with data
    data = iter('ABCD')
    res = padnone(data)
    assert next(res) == 'A'
    assert list(islice(res, 4)) == ['B', 'C', 'D', None]
    assert list(data) == []

    # padnone with empty
    data = ()
    res = padnone(data)
    assert next(res) is None
    assert list(islice(res, 4)) == [None, None, None, None]

def test_normal_peek():
    """Test padnone with peeking at iterable."""
    # padnone with data
    data = iter('ABCD')
    res = padnone(data)
    assert next(res) == 'A'
    assert next(data) == 'B'
    assert list(islice(res, 4)) == ['C', 'D', None, None]
    assert list(data) == []
