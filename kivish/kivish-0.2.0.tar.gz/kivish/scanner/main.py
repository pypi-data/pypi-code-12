#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
from ..node import TreeBuilder, PrimaryNodesLocator
from kivish.utils import error


class Scanner:
    '''Scans a kvs code to build a tree of nodes.'''

    def __init__(self, code):
        self._code = code

    def scan(self):
        '''
        Builds a tree of nodes. Returns a root node and a list
        of raw text lines.
        '''
        r = PrimaryNodesLocator(self._code).locate()
        root_tree, rules, raw = r['root'], r['rules'], r['raw']

        if not root_tree:
            error.report('no root node found')

        root = TreeBuilder(root_tree, rules).go()
        return {'root': root, 'raw': raw}
