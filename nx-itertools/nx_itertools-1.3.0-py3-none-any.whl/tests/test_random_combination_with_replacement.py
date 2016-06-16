"""Test for nx_itertools.recipes.random_combination_with_replacement"""
from unittest import mock
import pytest
from nx_itertools.recipes import random_combination_with_replacement


def test_normal():
    """Test random_combination_with_replacement."""
    with mock.patch('random.randrange', lambda x: 0):
        # combination with replacment, length of 1
        data = iter('ABC')
        res = random_combination_with_replacement(data, 1)
        assert res == ('A',)
        assert list(data) == []

        # combination with replacment, length of 2
        data = iter('ABC')
        res = random_combination_with_replacement(data, 2)
        assert res == ('A', 'A')
        assert list(data) == []

        # combination with replacment, length of 4
        data = iter('ABC')
        res = random_combination_with_replacement(data, 3)
        assert res == ('A', 'A', 'A')
        assert list(data) == []

        # combination with replacment, length of 4
        data = iter('ABC')
        res = random_combination_with_replacement(data, 4)
        assert res == ('A', 'A', 'A', 'A')
        assert list(data) == []

    # combination with replacment, length of 0
    data = iter('ABC')
    res = random_combination_with_replacement(data, 0)
    assert res == ()
    assert list(data) == []

    # combination with replacment of empty, length of 0
    data = ()
    res = random_combination_with_replacement(data, 0)
    assert res == ()

    # combination with replacment of empty, length of 1
    data = ()
    with pytest.raises(ValueError):
        random_combination_with_replacement(data, 1)


def test_oddity():
    """Test oddities of random_combination_with_replacement."""
    # combination with replacment, length of -1
    data = iter('ABC')
    res = random_combination_with_replacement(data, -1)
    assert res == ()
    assert list(data) == []

    # combination with replacment of empty, length of -1
    data = ()
    res = random_combination_with_replacement(data, -1)
    assert res == ()
