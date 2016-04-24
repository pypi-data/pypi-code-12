import struct
import array
import gzip
import numpy as np
from sets.core import Step, Dataset


class Mnist(Step):
    """
    The MNIST database of handwritten digits, available from this page, has a
    training set of 60,000 examples, and a test set of 10,000 examples. It is a
    subset of a larger set available from NIST. The digits have been
    size-normalized and centered in a fixed-size image. It is a good database
    for people who want to try learning techniques and pattern recognition
    methods on real-world data while spending minimal efforts on preprocessing
    and formatting. (From: http://yann.lecun.com/exdb/mnist/)
    """

    def __init__(self, provider='http://yann.lecun.com/exdb/mnist'):
        self._provider = provider

    def __call__(self):
        train = self.cache('train', self._train_dataset)
        test = self.cache('test', self._test_dataset)
        return train, test

    def _train_dataset(self):
        data = self.download(self._url('/train-images-idx3-ubyte.gz'))
        target = self.download(self._url('/train-labels-idx1-ubyte.gz'))
        return self._read_dataset(data, target)

    def _test_dataset(self):
        data = self.download(self._url('/t10k-images-idx3-ubyte.gz'))
        target = self.download(self._url('/t10k-labels-idx1-ubyte.gz'))
        return self._read_dataset(data, target)

    def _url(self, ressource):
        return self._provider + '/' + ressource

    @classmethod
    def _read_dataset(cls, data_filename, target_filename):
        data_array, data_size, rows, cols = cls._read_data(data_filename)
        target_array, target_size = cls._read_target(target_filename)
        assert data_size == target_size
        data = np.zeros((data_size, rows, cols))
        target = np.zeros((target_size, 10))
        for i in range(data_size):
            current = data_array[i * rows * cols:(i + 1) * rows * cols]
            data[i] = np.array(current).reshape(rows, cols) / 255
            target[i, target_array[i]] = 1
        return Dataset(data, target)

    @staticmethod
    def _read_data(filename):
        with gzip.open(filename, 'rb') as file_:
            _, size, rows, cols = struct.unpack('>IIII', file_.read(16))
            target = array.array('B', file_.read())
            assert len(target) == size * rows * cols
            return target, size, rows, cols

    @staticmethod
    def _read_target(filename):
        with gzip.open(filename, 'rb') as file_:
            _, size = struct.unpack('>II', file_.read(8))
            target = array.array('B', file_.read())
            assert len(target) == size
            return target, size
