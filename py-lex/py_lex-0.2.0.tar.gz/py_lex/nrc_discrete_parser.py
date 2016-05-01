# -*- coding: utf-8 -*-
'''
'''

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import (ascii, bytes, chr, dict, filter, hex, input,
                      int, map, next, oct, open, pow, range, round,
                      str, super, zip)

from itertools import groupby
from collections import defaultdict

class NrcDiscreteParser(object):

    '''
    liwc_lines: List[str] ->
    '''
    def __init__(self, nrc_lines):
        (self.parser, self.keys) = self._parse(nrc_lines)

    '''
    self[key]
    key: str -> Set[str]
    '''
    def __getitem__(self, key):
        return self.parser[key]

    '''
    key: str -> Set[str]
    '''
    def get_refs(self, key):
        return self.parser[key]

    '''
    '''
    def _parse(self, nrc_lines):
        split_lines = [ line.split('\t') for line in nrc_lines ]

        output = defaultdict(set)
        keys = set()

        for (token, attr, boolean) in split_lines:
            keys |= set([attr])
            if int(boolean) is 1:
                output[token] = output[token] | set([attr])

        return output, keys
