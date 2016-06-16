"""Test for nx_itertools.recipes.random_permutation"""
from itertools import islice
from unittest import mock
import pytest
from nx_itertools.recipes import random_permutation


def test_normal():
    """Test random_permutation."""
    with mock.patch('random.sample', lambda x, r: list(islice(x, r))):
        # permutation of three, no length
        data = iter('ABC')
        res = random_permutation(data)
        assert res == ('A', 'B', 'C')
        assert list(data) == []

        # permutation of three, length of 1
        data = iter('ABC')
        res = random_permutation(data, 1)
        assert res == ('A',)
        assert list(data) == []

        # permutation of three, length of 2
        data = iter('ABC')
        res = random_permutation(data, 2)
        assert res == ('A', 'B')
        assert list(data) == []

        # permutation of three, length of 3
        data = iter('ABC')
        res = random_permutation(data, 3)
        assert res == ('A', 'B', 'C')
        assert list(data) == []

    # permutation of three, length of 4
    data = iter('ABC')
    with pytest.raises(ValueError):
        random_permutation(data, 4)
    assert list(data) == []

    # permutation of three, length of 0
    data = iter('ABC')
    res = random_permutation(data, 0)
    assert res == ()
    assert list(data) == []

    # permutation with empty, no length
    data = ()
    res = random_permutation(data)
    assert res == ()

    # permutation with empty, length of 0
    data = ()
    res = random_permutation(data, 0)
    assert res == ()

    # permutation with empty, length of 1
    data = ()
    with pytest.raises(ValueError):
        random_permutation(data, 1)
