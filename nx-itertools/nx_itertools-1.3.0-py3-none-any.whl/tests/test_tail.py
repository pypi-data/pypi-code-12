"""Test for nx_itertools.recipes.tail"""
from nx_itertools.recipes import tail


def test_normal():
    """Test tail."""
    # tail less than data
    data = iter('ABCDE')
    res = tail(3, data)
    assert next(res) == 'C'
    assert list(res) == ['D', 'E']
    assert list(data) == []

    # tail exact count of data
    data = iter('ABCDE')
    res = tail(5, data)
    assert next(res) == 'A'
    assert list(res) == ['B', 'C', 'D', 'E']
    assert list(data) == []

    # tail more than data
    data = iter('ABCDE')
    res = tail(7, data)
    assert next(res) == 'A'
    assert list(res) == ['B', 'C', 'D', 'E']
    assert list(data) == []

    # tail nothing
    data = iter('ABCDE')
    res = tail(0, data)
    assert list(res) == []
    assert list(data) == []

    # empty but request some
    data = ()
    res = tail(3, data)
    assert list(res) == []

    # empty and request none
    data = ()
    res = tail(0, data)
    assert list(res) == []


def test_oddity():
    """Test oddities of tail."""
    data = iter('ABCDE')
    # specifying None as the length consumes the whole iterator
    res = tail(None, data)
    assert next(res) == 'A'
    assert list(res) == ['B', 'C', 'D', 'E']
    assert list(data) == []

    data = ()
    # specifying None as the length consumes the whole iterator
    res = tail(None, data)
    assert list(res) == []
