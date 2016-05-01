# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import (ascii, bytes, chr, dict, filter, hex, input,
                      int, map, next, oct, open, pow, range, round,
                      str, super, zip)

import re
import json
import pickle

from collections import Counter, defaultdict, ChainMap
from itertools import chain

from py_lex.liwc_parser import LiwcParser

class Liwc(object):

    punctuation = [
        ('period', '.'),
        ('comma', ','),
        ('colon', ':'),
        ('semic', ';'),
        ('qmark', '?'),
        ('exclam', '!'),
        ('dash', '-'),  # –—
        ('quote', '"'),  # “”
        ('apostro', "'"),  # ‘’
        ('parenth', '()[]{}'),
        ('otherp', '#$%&*+-/<=>@\\^_`|~'),
    ]

    def __init__(self, liwc_filepath=None):

        if liwc_filepath:
            with open(liwc_filepath) as liwc_file:
                self.parser = self._load_and_parse(liwc_file)

    '''
    token: str -> Set(str)
    '''
    def categorize_token(self, token):
        return self.parser[token]

    '''
    For each word string return a tuple (str, Set()) in place.

    [
        ['a', 'tokenized', 'sentence', '.'],
        ['within', 'a', 'single', 'document', '.'],
        ...
    ]
    ->
    [
        [Set('pronoun'), ...],
        ...
    ]
    doc: List[List[str]], ignore_sentences: Bool || True ->
        List[List[Set(str)]]
    '''
    def annotate_doc(self, doc, ignore_sentences=True):
        if ignore_sentences:
            return [ self.categorize_token(word.lower()) for word in doc ]
        else:
            return [ [ self.categorize_token(word.lower()) for word in sent ]
                    for sent in doc ]

    '''
    @XXX does not support sentence level statistics yet

    doc: List[List[str]], ignore_sentences: Bool || True ->
        Counter(key, int)
    '''
    def summarize_doc(self, doc, ignore_sentences=True):
        annotation = self.annotate_doc(doc, ignore_sentences)

        # return just the summarization
        return self.summarize_annotation(annotation)[0]

    def summarize_annotation(self, annotation, doc):
        # Strip punctuation for word counts
        wc = len([w for w in doc if re.match('\w+', w)])

        sixltr = sum(len(token) > 6 for token in doc)
        numerals = sum(token.isdigit() for token in doc)
        punct_counts = self._count_punctuation(doc)

        ctr = Counter(list(self._flatten_list_of_sets(annotation)))

        # convert counts to percentile dict
        percent_dict = {k: float(v)/float(wc) for (k,v) in dict(ctr).items()}

        # add non-percentile measures
        percent_dict['wc'] = wc
        percent_dict['analytic'] = self.analytic_thinking_score(percent_dict)
        percent_dict['tone'] = self.emotional_tone_score(percent_dict)
        percent_dict['authentic'] = self.authenticity_score(percent_dict)
        percent_dict['sixltr'] = sixltr
        percent_dict['numerals'] = numerals
        percent_dict['allpct'] = sum(punct_counts.values())

        # Merge the two dictionaries
        return (annotation, dict(ChainMap(percent_dict, punct_counts)))

    '''
    Where percentile_dict is a dict of percentiles of word per document

    Equivalent to LIWC2015 Analytic Thinking category, previously referred to
    as the Category Dimension Index from:

    Pennebaker J. W., Chung C. K. , Frazee J. , Lavergne G. M.,
    and Beaver D. I. (2014). When small words foretell academic success:
    The case of college admissions essays.
    PLoS ONE 9(12): e115844. doi: 10.1371/journal.pone.0115844.
    '''
    def analytic_thinking_score(self, percentile_dict):
        c = defaultdict(lambda: 0, percentile_dict)
        return 0.3 + c['article'] + c['preps'] - c['ppron'] - c['ipron'] \
            - c['auxverb'] - c['conj'] - c['adverb'] - c['negate']

    '''
    Where percentile_dict is a dict of percentiles of word per document

    Roughly equivalent to LIWC2015 Emotional Tone category, see:

    Cohn, M.A., Mehl, M.R., & Pennebaker, J.W. (2004).
    Linguistic Markers of Psychological Change Surrounding
    September 11, 2001. Psychological Science, 15, 687-693.
    '''
    def emotional_tone_score(self, percentile_dict):
        c = defaultdict(lambda: 0, percentile_dict)
        # Social + Emotional Positivity + CogMech + Psychological Distance
        return (c['we'] + c['social']) + \
               (c['posemo'] - c['negemo']) + \
               c['cogmech'] + \
               c['articles'] + c['sixltr'] + \
               -0.05 * c['present'] + -0.05 * c['i']

    '''
    Where percentile_dict is a dict of percentiles of word per document

    Equivalent to LIWC2015 Authenticity category, see Table 4 in:

    Newman, M.L., Pennebaker, J.W., Berry, D.S., & Richards, J.M. (2003).
    Lying words: Predicting deception from linguistic styles.
    Personality and Social Psychology Bulletin, 29, 665-675.
    '''
    def authenticity_score(self, percentile_dict):
        c = defaultdict(lambda: 0, percentile_dict)
        return 0.36 * (c['i'] + c['we']) + \
               0.16 * (c['shehe'] + c['they']) + \
               -0.15 * c['negemo'] + \
               0.54 + c['excl'] + \
               -0.2 + c['motion'] 

    '''
    Could not determine formula for clout from cited paper:

    Kacewicz, W., Pennebaker, J.W., Davis, M., Jeon, M., & Graesser, A.C.
    (2013). Pronoun use reflects standings in social hierarchies.
    Journal of Language and Social Psychology.
    Online version 19 September 2013, DOI: 10.1177/0261927X1350265.
    '''
    # def clout_score(self, percentile_dict):
    #     c = defaultdict(lambda: 0, percentile_dict)
    #     return c['i'] * -0.85 + c['we'] * 0.49 + c['shehe'] * 0.29

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

    '''
    l_of_s: List[List[Set[str]]] -> generator List[str]
    '''
    def _flatten_list_of_list_of_sets(self, l_of_l_of_s):
        return chain.from_iterable(
                    self._flatten_list_of_sets(l_of_l_of_s))

    '''
    Reads the LIWC file format:

        %
        1   funct
        2   pronoun
        %
        a   1   10
        abdomen*    146 147
        about   1   16  17

    Returns a parser object that can tell the LIWC categories of a
    given word efficiently.
    '''
    def _load_and_parse(self, liwc_file):
        return LiwcParser(liwc_file.read().splitlines())

    def _count_punctuation(self, doc):
        return { k: sum(1 for token in doc if token in p)
                            for (k, p) in self.punctuation  }

