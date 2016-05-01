# -*- coding: utf-8 -*-
'''
An immutable LIWC corpus container. Uses dictionary for exact match strings
and a Trie for finding matching stems (or prefixes).

Instantiate with a list of lines from a LIWC-formatted dataset.

For example, when given a LIWC file of the form:

>>> liwc_lines = [ "%", \
        "1 I", "2 me", "3 my", "4 we", "7 singular", "8 plural", "9 possessive", \
        "%", \
        "me 2 7", "mine 3 7 9", "my 3 7 9", "myself 2 7", \
        "our 6 8 9", "us 5 8", "we’* 4 8", ]
>>> example = LiwcParser(liwc_lines)

# Use __getitem__(key) magic method to retrieve the sets for a word
>>> example['my']
set(['my', 'singular'])

# __getitem__ returns the empty set for non-existing entries
>>> example['nowhere']
set([])

# Use .get_refs(key) to get the internal LIWC number
>>> example.get_refs('my')
set([3])

# __len__ returns the number of entries not categories
>>> len(example)
7
'''

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import (ascii, bytes, chr, dict, filter, hex, input,
                      int, map, next, oct, open, pow, range, round,
                      str, super, zip)

from bidict import frozenbidict
from marisa_trie import Trie

class LiwcParser(object):

    '''
    liwc_lines: List[str] ->
    '''
    def __init__(self, liwc_lines):
        (self.category_bidict,
        self.stem_to_categories,
        self.direct_lookup_stems,
        self.stem_search_trie) = self._parse(liwc_lines)

    '''
    self[key]
    key: str -> Set[str]
    '''
    def __getitem__(self, key):
        # Convert categories from ints to string representations
        return set(self.category_bidict[ref] for ref in self.get_refs(key))

    '''
    key: str -> Set[int]
    '''
    def get_refs(self, key):
        categories = set()
        stems = self.stem_search_trie.prefixes(key)

        if key in self.direct_lookup_stems:
            categories |= self.stem_to_categories[key]

        if stems is not None:
            for stem in stems:
                categories |= self.stem_to_categories[stem]

        return categories

    '''
    Returns:
        category_ref_bidict: one-to-one mapping of ints to categories
        stem_to_categories: all stem/words to their categories as a set
        stem_lookup: list of strings that are dictionary lookup-able stems
        stem_search_trie: trie to search through for all the other stems

    liwc_lines: List[str] -> Tuple(frozenbidict[int, str],
                                   Dict[str, Set(int)],
                                   List[str],
                                   Trie[str])
    '''
    def _parse(self, liwc_lines):
        categories, stems = self._get_category_and_stem_lines(liwc_lines)

        category_ref_bidict = self._build_category_ref_bidict(categories)
        stem_to_categories = self._build_stem_cat_dict(stems)
        stem_search, stem_lookup = self._build_stem_key_lists(stems)
        stem_search_trie = self._build_stem_trie(stem_search)

        return ( category_ref_bidict, stem_to_categories,
                 stem_lookup, stem_search_trie )

    def _get_category_indices(self, liwc_lines):
        divider_start, divider_stop = \
            tuple(i for i, char in enumerate(liwc_lines) if char is '%') 
        # because this is for slicing which is exclusive ranges we do not pad
        # the upper limit
        return divider_start + 1, divider_stop

    def _get_category_and_stem_lines(self, liwc_lines):
        cat_start, cat_end = self._get_category_indices(liwc_lines)
        categories = [l.split() for l in liwc_lines[cat_start:cat_end]]
        stems = [l.split() for l in liwc_lines[cat_end+1:]]
        return (categories, stems)

    '''
    Returns a frozenbidict, which is an immutable bidirectional dictionary,
    which can be queried directly for ints result[1] or through result.inv['me']
    for the category names.

    [['1', 'funct'], ...] -> {1: 'funct', ...}
    category_lines: List[List[str, str]] -> Bidict
    '''
    def _build_category_ref_bidict(self, category_lines):
        return frozenbidict({ int(cat[0]):cat[1] for cat in category_lines })

    '''
    [['stem*', '1', '3', ...], ...] ->
    { 'stem': set([1, 3, ...]), ...}
    '''
    def _build_stem_cat_dict(self, stem_lines):
        return { stem[0].rstrip('*'): set(int(x) for x in stem[1:])
                    for stem in stem_lines }

    '''
    Separate simple word lookup (where we can use a dictionary directly) from
    stems which need to be searched for in a trie

    [['stem', '1', '3', ...], ['stemi*', '2'] ...] ->
    ( {'stem', ...}, {'stemi', ...} )
    '''
    def _build_stem_key_lists(self, stem_lines):
        stems, keys = [], []
        endswith_star = lambda s: str.endswith(s, '*')
        
        for stem in stem_lines:
            (stems if endswith_star(stem[0]) else keys) \
                .append(stem[0].rstrip('*'))

        return set(stems), set(keys)
    
    '''
    Marisa trie for stem lookup,
    e.g. trie.prefixes('thanksgiving') -> ['thank', 'thanks']
    stem_search: Set(str) -> Trie
    '''
    def _build_stem_trie(self, stem_search):
        return Trie(stem_search)

