import numpy as np
from sets.core import Embedding


class OneHot(Embedding):

    def __init__(self, words, embed_data=False, embed_target=False):
        table = self._construct_table(words)
        super().__init__(table, len(table), embed_data, embed_target)

    def lookup(self, word):
        return super().lookup(self._obtain_key(word))

    @classmethod
    def _construct_table(cls, words):
        table = {}
        for word in words:
            key = cls._obtain_key(word)
            if key in table:
                continue
            vector = np.zeros(len(words))
            vector[len(table)] = 1
            table[key] = vector
        return table

    @staticmethod
    def _obtain_key(word):
        if isinstance(word, np.ndarray):
            return word.tostring()
        return word
