"""Test for nx_itertools.recipes.all_equal"""
from nx_itertools.recipes import all_equal


def test_normal_equal():
    """Test all_equal."""
    # all_equal with success
    data = iter('AAAAA')
    res = all_equal(data)
    assert res is True
    assert list(data) == []

    # all_equal with no success
    data = iter('AAAAB')
    res = all_equal(data)
    assert res is False
    assert list(data) == []

    # all_equal with empty
    data = ()
    res = all_equal(data)
    assert res is True


def test_oddity():
    """Test oddities of all_equal."""
    # all_equal doesn't consume the iterator after the first non-equal
    data = iter('ABCD')
    res = all_equal(data)
    assert res is False
    assert list(data) == ['C', 'D']
