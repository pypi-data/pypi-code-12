# -*- coding: utf-8 -*-
'''
'''
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import (ascii, bytes, chr, dict, filter, hex, input,
                      int, map, next, oct, open, pow, range, round,
                      str, super, zip)

from collections import Counter, ChainMap
from itertools import chain
import re
import pickle

from py_lex.nrc_discrete_parser import NrcDiscreteParser

class EmoLex(object):

    def __init__(self, emolex_filepath=None):

        if emolex_filepath:
            with open(emolex_filepath) as emolex_file:
                self.parser = self._load_and_parse(emolex_file)

    def __len__(self):
        return len(self.keys())

    def keys(self):
        return self._parser_keys()

    def _parser_keys(self):
        return self.parser.keys

    def categorize_token(self, token):
        return self.parser[token.lower()]

    def annotate_doc(self, doc):
        return [ self.categorize_token(word.lower()) for word in doc ]

    def summarize_doc(self, doc):
        annotation = self.annotate_doc(doc)

        # return just the summarization
        return self.summarize_annotation(annotation, doc)

    def summarize_annotation(self, annotation, doc):
        wc = len([w for w in doc if re.match('\w+', w)])
        ctr = Counter(list(self._flatten_list_of_sets(annotation)))

        # Convert to percentiles
        summary = {k: float(v)/float(wc) for (k,v) in dict(ctr).items()}

        # Set keys that did not occur to 0
        not_counted = { k: 0.0 for k in
                self._parser_keys() - set(summary.keys()) }

        # Merge the two dictionaries
        return dict(ChainMap(summary, not_counted))

    def load(self, pickle_filepath):
        with open(pickle_filepath, 'rb') as pickle_file:
            self.parser = pickle.load(pickle_file)

    def dump(self, pickle_filepath):
        with open(pickle_filepath, 'wb') as pickle_file:
            pickle.dump(self.parser, pickle_file)

    '''
    l_of_s: List[Set[str]] -> generator List[str]
    '''
    def _flatten_list_of_sets(self, l_of_s):
        return chain.from_iterable([ list(categories)
            for categories in l_of_s ])

    def _load_and_parse(self, emolex_file):
        return NrcDiscreteParser(emolex_file.read().splitlines())
