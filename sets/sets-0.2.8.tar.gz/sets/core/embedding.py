import numpy as np
from sets.core import Step, Dataset


class Embedding(Step):
    """
    Step that replaces string words by numeric vectors, usually using a lookup
    table. The default fallback for unknown words is the average embedding
    vector and a zero vector for falsy words.
    """

    def __init__(self, table, dimensions, embed_data=False, embed_target=False):
        assert all(len(x) == dimensions for x in table.values())
        assert embed_data or embed_target
        ordered = sorted(table.keys())
        self._index = {k: i for i, k in enumerate(ordered)}
        self._embeddings = np.array([table[x] for x in ordered])
        self._dimensions = dimensions
        self._embed_data = embed_data
        self._embed_target = embed_target
        self._average = sum(table.values()) / len(table)

    def __call__(self, dataset):
        # pylint: disable=arguments-differ
        data = dataset.data
        target = dataset.target
        if self._embed_data:
            data = self._embed(data)
        if self._embed_target:
            target = self._embed(target)
        return Dataset(data, target)

    def __setitem(self, word, embedding):
        self._table[self.key(word)] = embedding

    def __getitem__(self, word):
        index = self._index[self.key(word)]
        embedding = self._embeddings[index]
        return embedding

    def __in__(self, word):
        return self.key(word) in self._index

    @property
    def dimensions(self):
        return self._dimensions

    def key(self, word):
        # Support embedding numpy vectors.
        if isinstance(word, np.ndarray):
            return word.tostring()
        return word

    def lookup(self, word):
        if word in self._index:
            return self[word]
        else:
            return self.fallback(word)

    def fallback(self, word):
        # pylint: disable=unused-argument
        if not word:
            return np.zeros(self.dimensions)
        return self._average

    def _embed(self, data):
        shape = data.shape + (self.dimensions,)
        embedded = np.empty(shape)
        for index, word in np.ndenumerate(data):
            embedded[index] = self.lookup(word)
        return embedded
