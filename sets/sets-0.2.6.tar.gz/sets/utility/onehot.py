import numpy as np
from sets.core import Embedding


class OneHot(Embedding):

    def __init__(self, words, embed_data=False, embed_target=False):
        keys = list(set(self._obtain_key(x) for x in words))
        table = self._construct_table(keys)
        super().__init__(table, len(keys), embed_data, embed_target)

    def lookup(self, word):
        return super().lookup(self._obtain_key(word))

    @classmethod
    def _construct_table(cls, keys):
        table = {}
        for key in sorted(keys):
            vector = np.zeros(len(keys))
            vector[len(table)] = 1
            table[key] = vector
        return table

    @staticmethod
    def _obtain_key(word):
        if isinstance(word, np.ndarray):
            return word.tostring()
        return word
