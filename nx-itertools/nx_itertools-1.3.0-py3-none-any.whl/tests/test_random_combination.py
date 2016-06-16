"""Test for nx_itertools.recipes.random_combination"""
from itertools import islice
from unittest import mock
import pytest
from nx_itertools.recipes import random_combination


def test_normal():
    """Test random_combination."""
    with mock.patch('random.sample', lambda x, r: list(islice(x, r))):
        # combination with length of 1
        data = iter('ABC')
        res = random_combination(data, 1)
        assert res == ('A',)
        assert list(data) == []

        # combination with length of 2
        data = iter('ABC')
        res = random_combination(data, 2)
        assert res == ('A', 'B')
        assert list(data) == []

        # combination with length of 3
        data = iter('ABC')
        res = random_combination(data, 3)
        assert res == ('A', 'B', 'C')
        assert list(data) == []

    # combination with length of 4
    data = iter('DEF')
    with pytest.raises(ValueError):
        random_combination(data, 4)
    assert list(data) == []

    # combination with length of 0
    data = iter('DEF')
    res = random_combination(data, 0)
    assert res == ()
    assert list(data) == []

    # combination of empty with length of 0
    data = ()
    res = random_combination(data, 0)
    assert res == ()

    # combination of empty with length of 1
    data = ()
    with pytest.raises(ValueError):
        random_combination(data, 1)
