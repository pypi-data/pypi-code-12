"""Test for nx_itertools.recipes.first_true"""
from nx_itertools.recipes import first_true


def test_normal():
    """Test first_true."""
    # first_true with success
    data = iter([0, 0, 'A', 0])
    res = first_true(data)
    assert res == 'A'
    assert list(data) == [0]

    # first_true with no success
    data = iter([0, 0, 0, 0])
    res = first_true(data)
    assert res is False
    assert list(data) == []

    # first_true with empty
    data = ()
    res = first_true(data)
    assert res is False

    # first_true with predicate and success
    data = iter('ABCDE')
    res = first_true(data, pred=lambda x: x == 'D')
    assert res == 'D'
    assert list(data) == ['E']

    # first_true with predicate and no success
    data = iter('ABCDE')
    res = first_true(data, pred=lambda x: x == 'X')
    assert res is False
    assert list(data) == []

    # first_true with no success and default
    data = iter([0, 0, 0, 0])
    res = first_true(data, default='X')
    assert res == 'X'
    assert list(data) == []

    # first_true with empty and default
    data = ()
    res = first_true(data, default='X')
    assert res == 'X'

    # first_true with predicate, no success, and default
    data = iter('ABCDE')
    res = first_true(data, default='Q', pred=lambda x: x == 'X')
    assert res == 'Q'
    assert list(data) == []

    # first_true with empty, predicate, no success, and default
    data = ()
    res = first_true(data, default='Q', pred=lambda x: x == 'X')
    assert res == 'Q'
