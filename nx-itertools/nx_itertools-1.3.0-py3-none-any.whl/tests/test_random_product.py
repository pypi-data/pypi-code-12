"""Test for nx_itertools.recipes.random_product"""
from unittest import mock
import pytest
from nx_itertools.recipes import random_product


def test_normal():
    """Test random_product."""
    with mock.patch('random.choice', lambda x: x[0]):
        # product to 4x2 with no repeat
        data1, data2 = iter('ABCD'), iter('xy')
        res = random_product(data1, data2)
        assert res == ('A', 'x')
        assert list(data1) == []
        assert list(data2) == []

        # product to 4x2 with repeat of 1
        data1, data2 = iter('ABCD'), iter('xy')
        res = random_product(data1, data2, repeat=1)
        assert res == ('A', 'x')
        assert list(data1) == []
        assert list(data2) == []

        # product to 4x2 with repeat of 2
        data1, data2 = iter('ABCD'), iter('xy')
        res = random_product(data1, data2, repeat=2)
        assert res == ('A', 'x', 'A', 'x')
        assert list(data1) == []
        assert list(data2) == []

        # product to 4x2 with repeat of 0
        data1, data2 = iter('ABCD'), iter('xy')
        res = random_product(data1, data2, repeat=0)
        assert res == ()
        assert list(data1) == []
        assert list(data2) == []

        # product of 4 with no repeat
        data = iter('ABCD')
        res = random_product(data)
        assert res == ('A',)
        assert list(data) == []

        # product of 4 with repeat of 1
        data = iter('ABCD')
        res = random_product(data, repeat=1)
        assert res == ('A',)
        assert list(data) == []

        # product of 4 with repeat of 2
        data = iter('ABCD')
        res = random_product(data, repeat=2)
        assert res == ('A', 'A')
        assert list(data) == []

    # no data with no repeat
    res = random_product()
    assert res == ()

    # no data with repeat of 2
    res = random_product(repeat=2)
    assert res == ()

    # product with one empty
    data1, data2 = iter('ABCD'), ()
    with pytest.raises(IndexError):
        random_product(data1, data2)
    assert list(data1) == []

    # product with one empty
    data1, data2 = (), iter('ABCD')
    with pytest.raises(IndexError):
        random_product(data1, data2)
    assert list(data2) == []

    # empty
    data = ()
    with pytest.raises(IndexError):
        random_product(data)


def test_oddity():
    """Test oddities of random_product."""
    # no data with negative repeat
    res = random_product(repeat=-1)
    assert res == ()

    with mock.patch('random.choice', lambda x: x[0]):
        # product of 4 with negative repeat
        data = iter('ABCD')
        res = random_product(data, repeat=-1)
        assert res == ()
        assert list(data) == []

        # product with one empty and negative repeat
        data = ()
        res = random_product(data, repeat=-1)
        assert res == ()
