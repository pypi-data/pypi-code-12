"""Test for nx_itertools.recipes.take"""
from nx_itertools.recipes import take


def test_normal():
    """Test take."""
    # take less than data
    data = iter('ABCDE')
    res = take(3, data)
    assert res == ['A', 'B', 'C']
    assert list(data) == ['D', 'E']

    # take exact count of data
    data = iter('ABCDE')
    res = take(5, data)
    assert res == ['A', 'B', 'C', 'D', 'E']
    assert list(data) == []

    # take more than data
    data = iter('ABCDE')
    res = take(7, data)
    assert res == ['A', 'B', 'C', 'D', 'E']
    assert list(data) == []

    # take nothing
    data = iter('ABCDE')
    res = take(0, data)
    assert res == []
    assert list(data) == ['A', 'B', 'C', 'D', 'E']

    # empty but request some
    data = ()
    res = take(3, data)
    assert res == []

    # empty and request none
    data = ()
    res = take(0, data)
    assert res == []


def test_oddity():
    """Test oddities of take."""
    data = iter('ABCDE')
    # specifying None as the length consumes the whole iterator
    res = take(None, data)
    assert res == ['A', 'B', 'C', 'D', 'E']
    assert list(data) == []

    data = ()
    # specifying None as the length consumes the whole iterator
    res = take(None, data)
    assert res == []
