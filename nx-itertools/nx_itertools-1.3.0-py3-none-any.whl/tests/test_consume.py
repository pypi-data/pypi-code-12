"""Test for nx_itertools.recipes.consume"""
from nx_itertools.recipes import consume


def test_normal():
    """Test consume."""
    # consume less than data
    data = iter('ABCDE')
    consume(data, 3)
    assert list(data) == ['D', 'E']

    # consume exact count of data
    data = iter('ABCDE')
    consume(data, 5)
    assert list(data) == []

    # consume more than data
    data = iter('ABCDE')
    consume(data, 7)
    assert list(data) == []

    # empty but consume some
    data = ()
    consume(data, 5)
    assert list(data) == []

    # None consumes all
    data = iter('ABCDE')
    consume(data, None)
    assert list(data) == []

    # empty but consume all
    data = ()
    consume(data, None)
    assert list(data) == []

    # consume nothing
    data = iter('ABCDE')
    consume(data, 0)
    assert list(data) == ['A', 'B', 'C', 'D', 'E']

    # empty and consume nothing
    data = ()
    consume(data, 0)
    assert list(data) == []
