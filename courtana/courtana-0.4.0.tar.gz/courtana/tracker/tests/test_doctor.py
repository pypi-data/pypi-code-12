import numpy as np

from ..doctor import _cover_neighbors


def test_cover_one_neighbor():
    a = np.array([0, 5, 8])
    covered = _cover_neighbors(a, n=1)
    expected = np.array([0, 1, 4, 5, 6, 7, 8])
    assert np.array_equal(covered, expected)


def test_cover_two_neighbors():
    a = np.array([0, 5, 8])
    covered = _cover_neighbors(a, n=2)
    expected = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8])
    assert np.array_equal(covered, expected)


def test_cover_neighbor_true_min():
    a = np.array([1, 4])
    covered = _cover_neighbors(a, n=1, true_min=0)
    expected = np.array([0, 1, 2, 3, 4])
    assert np.array_equal(covered, expected)


def test_cover_neighbor_true_max():
    a = np.array([1, 4])
    covered = _cover_neighbors(a, n=1, true_max=10)
    expected = np.array([1, 2, 3, 4, 5])
    assert np.array_equal(covered, expected)
