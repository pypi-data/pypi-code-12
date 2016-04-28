import numpy as np
from sets.core import Step, Dataset


class Embedding(Step):
    """
    Step that replaces string words by numeric vectors, usually using a lookup
    table. This may be used for hot-word encoding or vector space embeddings.
    """

    def __init__(self, table, dimensions, embed_data=False, embed_target=False):
        assert all(len(x) == dimensions for x in table.values())
        assert embed_data or embed_target
        self._table = table
        self._dimensions = dimensions
        self._embed_data = embed_data
        self._embed_target = embed_target
        self._average = sum(table.values()) / len(table)

    def __call__(self, dataset):
        # pylint: disable=arguments-differ
        data = dataset.data
        target = dataset.target
        if self._embed_data:
            data = self._replace(data)
        if self._embed_target:
            target = self._replace(target)
        return Dataset(data, target)

    def __setitem(self, word, embedding):
        self._table[word] = embedding

    def __getitem__(self, word):
        return self._table[word]

    def __in__(self, word):
        return word in self._table

    @property
    def dimensions(self):
        return self._dimensions

    def lookup(self, word):
        if word in self._table:
            return self._table[word]
        else:
            return self.fallback(word)

    def fallback(self, word):
        # pylint: disable=unused-argument
        return self._average

    def _replace(self, data):
        shape = data.shape + (self.dimensions,)
        replaced = np.empty(shape)
        for index, word in np.ndenumerate(data):
            replaced[index] = self.lookup(word)
        return replaced
