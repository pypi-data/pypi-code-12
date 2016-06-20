#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
from .analyzer import Analyzer
from ..node import TreeBuilder, PrimaryNodesLocator


class Scanner:
    '''Scans a kvs code to build a tree of nodes.'''

    def __init__(self, code):
        Analyzer(code).check()
        self.code = code

    def scan(self):
        '''Builds a tree of nodes and returns a root node.'''
        data = PrimaryNodesLocator(self.code).locate()
        root_tree, rules = data['root'], data['rules']
        return TreeBuilder(root_tree, rules).go()
