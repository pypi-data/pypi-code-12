"""Test for nx_itertools.recipes.unique_everseen"""
from nx_itertools.recipes import unique_everseen


def test_normal():
    """Test unique_everseen."""
    # no key with all upper data
    data = iter('AAAABBBCCDAABBB')
    res = unique_everseen(data)
    assert next(res) == 'A'
    assert list(res) == ['B', 'C', 'D']
    assert list(data) == []

    # no key with mixed data
    data = iter('AAAABBBcCcCDAABBB')
    res = unique_everseen(data)
    assert next(res) == 'A'
    assert list(res) == ['B', 'c', 'C', 'D']
    assert list(data) == []

    # lower key with mixed data - note key is unchanged from first instance
    data = iter('ABBCcAD')
    res = unique_everseen(data, lambda x: x.lower())
    assert next(res) == 'A'
    assert list(res) == ['B', 'C', 'D']
    assert list(data) == []

    # lower key with mixed data - note key is unchanged from first instance
    data = iter('ABBcCcCAD')
    res = unique_everseen(data, lambda x: x.lower())
    assert next(res) == 'A'
    assert list(res) == ['B', 'c', 'D']
    assert list(data) == []

    # empty
    data = ()
    res = unique_everseen(data)
    assert list(res) == []


def test_normal_peek():
    """Test unique_everseen with peeking at iterable."""
    # no key with all upper data
    data = iter('ABAACCD')
    res = unique_everseen(data)
    assert next(res) == 'A'
    assert next(data) == 'B'
    assert list(res) == ['C', 'D']
    assert list(data) == []

    # no key with mixed data
    data = iter('ABCcAD')
    res = unique_everseen(data, lambda x: x.lower())
    assert next(res) == 'A'
    assert next(data) == 'B'
    assert list(res) == ['C', 'D']
    assert list(data) == []

    # lower key with mixed data - note key is unchanged from first instance
    data = iter('ABcCcCAD')
    res = unique_everseen(data, lambda x: x.lower())
    assert next(res) == 'A'
    assert next(data) == 'B'
    assert list(res) == ['c', 'D']
    assert list(data) == []

    # lower key with mixed data - note key is unchanged from first instance
    data = iter('ABBcCcCAD')
    res = unique_everseen(data, lambda x: x.lower())
    assert next(res) == 'A'
    assert next(data) == 'B'
    assert list(res) == ['B', 'c', 'D'] # first B removed but second is still
                                        # there
    assert list(data) == []
