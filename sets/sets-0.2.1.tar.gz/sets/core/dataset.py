import random
import numpy as np


class Dataset:
    """
    Two immutable Numpy arrays holding data and targets of a dataset.
    """

    def __init__(self, data, target):
        """
        Data and target are expected to each be either Numpy arrays or
        filenames to Numpy arrays. Both must be of the same length.
        """
        # pylint: disable=redefined-variable-type
        if isinstance(data, str):
            data = np.load(data)
        if isinstance(target, str):
            target = np.load(target)
        data = np.array(data)
        target = np.array(target)
        assert len(data) == len(target)
        data.setflags(write=False)
        target.setflags(write=False)
        self._data = data
        self._target = target

    @property
    def data(self):
        return self._data

    @property
    def target(self):
        return self._target

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        yield from zip(self.data, self.target)

    def random_batch(self, size):
        indices = random.sample(range(len(self)), size)
        return self.data[indices], self.target[indices]

    def save(self, prefix):
        np.save(prefix + '-data.npy', self._data)
        np.save(prefix + '-target.npy', self._target)

    @classmethod
    def load(cls, prefix):
        return cls(prefix + '-data.npy', prefix + '-target.npy')
