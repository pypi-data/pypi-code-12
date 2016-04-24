import numpy as np
import pytest
import sets
from sets import Dataset


@pytest.fixture
def dataset():
    data = [[1, 3], [0, -1], [0, 0]]
    target = [0, 0.5, 1]
    return Dataset(data, target)


def test_concat(dataset):
    other = Dataset([[1], [2], [3]], [0.5, 2, -1])
    result = sets.Concat(target_from=1, axis=1)(dataset, other)
    assert (result.target == other.target).all()
    assert len(result) == len(dataset)
    assert result.data.shape[1] == dataset.data.shape[1] + 1
    assert (result.data[:, :-1] == dataset.data).all()
    assert (result.data[:, -1] == other.data[:, 0]).all()


def test_onehot(dataset):
    result = sets.OneHot(dataset.data, embed_target=True)(dataset)
    assert result.target.shape[1] == len(np.unique(dataset.target))
    assert (result.target.sum(axis=1) == 1).all()


def test_split(dataset):
    one, two, three = sets.Split(0.33, 0.66)(dataset)
    assert len(one) + len(two) + len(three) == len(dataset)
    data = np.concatenate((one.data, two.data, three.data))
    target = np.concatenate((one.target, two.target, three.target))
    assert (data == dataset.data).all()
    assert (target == dataset.target).all()


def test_normalize(dataset):
    width = dataset.data.shape[1]
    normalize = sets.Normalize(dataset)
    result = normalize(dataset)
    assert np.allclose(result.data.mean(axis=0), np.zeros(width))
    assert np.allclose(result.data.std(axis=0), np.ones(width))
    other = normalize(Dataset(dataset.data + 1, dataset.target))
    assert not np.allclose(other.data.mean(axis=0), np.zeros(width))
    assert np.allclose(other.data.std(axis=0), np.ones(width))


def test_shuffle(dataset):
    result = sets.Shuffle(seed=0)(dataset)
    assert result.data.shape == dataset.data.shape
    assert result.target.shape == dataset.target.shape
    in_sums = sorted([x.sum() + y.sum() for x, y in dataset])
    out_sums = sorted([x.sum() + y.sum() for x, y in result])
    assert in_sums == out_sums
