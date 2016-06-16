"""Test for nx_itertools.recipes.quantify"""
from nx_itertools.recipes import quantify


def test_normal_found():
    """Test quantify."""
    # quantify with match
    data = iter('ABACD')
    res = quantify(data, pred=lambda x: x == 'A')
    assert res == 2
    assert list(data) == []

    # quantify with no match
    data = iter('ABACD')
    res = quantify(data, pred=lambda x: x == 'X')
    assert res == 0
    assert list(data) == []

    # quantify empty
    data = ()
    res = quantify(data, pred=lambda x: x == 'X')
    assert res == 0
