#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
from .regex import pattern_label, pattern_class, pattern_id
from .helper_value_reader import ValueReader
from . import error


class LineInfo:
    '''
    Gives useful information about a given line of code, such as:
    - indent (number of spaces)
    - label (string; validated, might raise SyntaxError)
    - value (string)
    - inline attributes (list of tuples)
    '''

    @property
    def indent(self):
        line = self._line.rstrip()
        return len(line) - len(line.lstrip())

    @property
    def value(self):
        return ValueReader(self._line).read()

    @property
    def label(self):
        if not self._label:
            self._label = self._line.lstrip().split()[0].rstrip(':')
            self._check_label()
            return self._label
        else:
            return self._label

    def _check_label(self):
        '''Raises SyntaxError on failure.'''
        if not pattern_label.match(self.label):
            error.report('bad label (%s)' % self.label)

    @property
    def inline_attrs(self):
        '''
        Returns a dict with classes and id. Example:
        {
            'classes': ['class-a', class-b],
            'id': 'id-x'
        }
        '''
        return get_inline_classes_and_id(self._line)

    def __init__(self, line):
        self._line = line
        self._label = None


def get_inline_classes_and_id(line):
    classes = pattern_class.findall(line)
    id = pattern_id.findall(line)
    id = id[-1] if id else None
    return {'classes': classes, 'id': id}
