import numpy as np
from sets.core import Step, Dataset


class Shuffle(Step):

    def __init__(self, seed=0):
        self._random = np.random.RandomState(seed)

    def __call__(self, dataset):
        indices = self._random.permutation(len(dataset))
        data = dataset.data[indices]
        target = dataset.target[indices]
        return Dataset(data, target)
