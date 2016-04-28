import numpy as np
from sets.core import Embedding


class OneHot(Embedding):

    def __init__(self, words, embed_data=False, embed_target=False):
        table = self._construct_table(words)
        super().__init__(table, len(table), embed_data, embed_target)

    def _construct_table(self, words):
        keys = list(set(self.key(x) for x in words))
        table = {}
        for key in sorted(keys):
            vector = np.zeros(len(keys))
            vector[len(table)] = 1
            table[key] = vector
        return table

