"""Test for nx_itertools.recipes.nth"""
from nx_itertools.recipes import nth


def test_normal():
    """Test nth."""
    # 0th element
    data = iter('ABCDE')
    res = nth(data, 0)
    assert res == 'A'
    assert list(data) == ['B', 'C', 'D', 'E']

    # 2nd element
    data = iter('ABCDE')
    res = nth(data, 2)
    assert res == 'C'
    assert list(data) == ['D', 'E']

    # last element
    data = iter('ABCDE')
    res = nth(data, 4)
    assert res == 'E'
    assert list(data) == []

    # beyond data with no default
    data = iter('ABCDE')
    res = nth(data, 7)
    assert res is None
    assert list(data) == []

    # beyond data with default
    data = iter('ABCDE')
    res = nth(data, 10, 'X')
    assert res == 'X'
    assert list(data) == []

    # 0th element, empty with no default
    data = ()
    res = nth(data, 0)
    assert res is None

    # 2nd element, empty with no default
    data = ()
    res = nth(data, 2)
    assert res is None

    # 0th element, empty with default
    data = ()
    res = nth(data, 0, 'X')
    assert res == 'X'

    # 2nd element, empty with default
    data = ()
    res = nth(data, 2, 'X')
    assert res == 'X'


def test_oddity():
    """Test oddities of nth."""
    # None gets the first element
    data = iter('ABCDE')
    res = nth(data, None)
    assert res is 'A'
    assert list(data) == ['B', 'C', 'D', 'E']

    # None gets the first element but it's empty, no default
    data = ()
    res = nth(data, None)
    assert res is None

    # None gets the first element but it's empty, with default
    data = ()
    res = nth(data, None, 'X')
    assert res == 'X'
