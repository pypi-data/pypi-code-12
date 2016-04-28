import numpy as np
from sets.core import Step, Dataset


class TagDistance(Step):

    def __init__(self, *tags):
        self._tags = tags

    def __call__(self, dataset):
        # pylint: disable=arguments-differ
        shape = dataset.data.shape + (len(self._tags),)
        data = np.empty(shape)
        for index, tokens in enumerate(dataset.data):
            positions = self._positions(tokens)
            data[index] = self._relative_sequence(positions, len(tokens))
        return Dataset(data, dataset.target)

    def _positions(self, tokens):
        return [np.where(tokens == x)[0][0] for x in self._tags]

    @staticmethod
    def _relative_sequence(positions, length):
        sequence = np.empty((length, len(positions)))
        for index, position in enumerate(positions):
            for current in range(length):
                sequence[current][index] = index - position
        return sequence
