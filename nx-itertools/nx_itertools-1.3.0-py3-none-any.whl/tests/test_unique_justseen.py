"""Test for nx_itertools.recipes.unique_justseen"""
from nx_itertools.recipes import unique_justseen


def test_normal():
    """Test unique_justseen."""
    # no key with all upper data
    data = iter('AAAABBBCCDAABBB')
    res = unique_justseen(data)
    assert next(res) == 'A'
    assert list(res) == ['B', 'C', 'D', 'A', 'B']
    assert list(data) == []

    # no key with mixed data
    data = iter('ABBcCcCAD')
    res = unique_justseen(data)
    assert next(res) == 'A'
    assert list(res) == ['B', 'c', 'C', 'c', 'C', 'A', 'D']
    assert list(data) == []

    # lower key with all upper data
    data = iter('ABBCCCAD')
    res = unique_justseen(data, lambda x: x.lower())
    assert next(res) == 'A'
    assert list(res) == ['B', 'C', 'A', 'D']
    assert list(data) == []

    # lower key with mixed data - note key is unchanged from first instance
    data = iter('ABBcCcCAD')
    res = unique_justseen(data, lambda x: x.lower())
    assert next(res) == 'A'
    assert list(res) == ['B', 'c', 'A', 'D']
    assert list(data) == []

    # empty
    data = ()
    res = unique_justseen(data)
    assert list(res) == []


def test_normal_peek():
    """Test unique_justseen with peeking at iterable."""
    # no key with all upper data
    data = iter('ABAAACCDAABBB')
    res = unique_justseen(data)
    assert next(res) == 'A'
    assert next(data) == 'B'
    assert list(res) == ['C', 'D', 'A', 'B']
    assert list(data) == []

    # no key with mixed data
    data = iter('ABBcCcCAD')
    res = unique_justseen(data)
    assert next(res) == 'A'
    assert next(data) == 'B'
    assert list(res) == ['B', 'c', 'C', 'c', 'C', 'A', 'D']
    assert list(data) == []

    # lower key with all upper data
    data = iter('ABCCCAD')
    res = unique_justseen(data, lambda x: x.lower())
    assert next(res) == 'A'
    assert next(data) == 'B'
    assert list(res) == ['C', 'A', 'D']
    assert list(data) == []

    # lower key with mixed data - note key is unchanged from first instance
    data = iter('ABcCcCAD')
    res = unique_justseen(data, lambda x: x.lower())
    assert next(res) == 'A'
    assert next(data) == 'B'
    assert list(res) == ['c', 'A', 'D']
    assert list(data) == []
