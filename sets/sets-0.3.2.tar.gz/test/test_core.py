# pylint: disable=no-self-use
import pickle
import numpy as np
import pytest
from sets import Dataset


@pytest.fixture
def dataset():
    numbers = [0, 0.5, -1]
    arrays = np.random.random((3, 2))
    strings = ['hello', 'world', '!']
    return Dataset(numbers=numbers, arrays=arrays, strings=strings)


class TestDataset:

    def test_access_column_by_attribute(self, dataset):
        assert (dataset.numbers == dataset['numbers']).all()
        assert (dataset.arrays == dataset['arrays']).all()
        assert (dataset.strings == dataset['strings']).all()
        with pytest.raises(AttributeError):
            # pylint: disable=pointless-statement
            dataset.foo

    def test_sample(self, dataset):
        dataset.sample(2)

    def test_pickle(self, dataset):
        dumped = pickle.dumps(dataset)
        loaded = pickle.loads(dumped)
        assert loaded == dataset
