import re
import nltk
import numpy as np
from sets.core import Step, Dataset


class Tokenize(Step):

    _regex_tag = re.compile(r'<[^>]+>')

    def __call__(self, dataset):
        # pylint: disable=arguments-differ
        data = [list(self._process(x)) for x in dataset.data]
        data = self._pad(data)
        return Dataset(data, dataset.target)

    def tokenize(self, sentence):
        tokens = nltk.word_tokenize(sentence)
        tokens = [x.lower() for x in tokens]
        return tokens

    def _process(self, sentence):
        while True:
            match = self._regex_tag.search(sentence)
            if not match:
                yield from self.tokenize(sentence)
                return
            chunk = sentence[:match.start()]
            yield from self.tokenize(chunk)
            tag = match.group(0)
            yield tag
            sentence = sentence[(len(chunk) + len(tag)):]

    @staticmethod
    def _pad(data):
        width = max(len(x) for x in data)
        for index, tokens in enumerate(data):
            missing = width - len(tokens)
            data[index] += ['' for _ in range(missing)]
        return np.array(data)
