import numpy as np
from sets.core import Step, Dataset


class Concat(Step):

    def __init__(self, target_from=0, axis=1):
        self._target_from = target_from
        self._axis = axis

    def __call__(self, *datasets):
        data = np.concatenate([x.data for x in datasets], axis=self._axis)
        target = datasets[self._target_from].target
        return Dataset(data, target)
