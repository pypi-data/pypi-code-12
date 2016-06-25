#!/usr/bin/env python
import copy


class Variable(object):
    '''
    Variable class.
    '''
    # Class variable dictionary.
    _vars = {}

    def __init__(self, key, value=[]):
        # Deep copy of value (avoids issues with default argument).
        x = copy.deepcopy(value)
        # Store key values in class variable.
        if not isinstance(x, list):
            x = [x]
        self._vars[key] = x
        self._key = key

    def __str__(self):
        # Get current key value when evaluated as string.
        return ' '.join(self._vars[self._key])

    def __add__(self, other):
        # Append other variables to key variable list.
        if not isinstance(other, list):
            other = [other]
        self._vars[self._key] += other
        return self

    @classmethod
    def get(cls, key):
        '''
        Get class instance of existing key.
        '''
        # TODO: Handle KeyError.
        return cls(key, cls._vars[key])

    @classmethod
    def get_all(cls):
        '''
        Get variables dictionary with joined string values.
        '''
        d = {}
        for key, item in cls._vars.items():
            d[key] = str(Variable(key, item))
        return d

    @classmethod
    def save(cls, prefix='_'):
        '''
        Return variables dictionary with keys prefixed by character.
        '''
        d = {}
        for key, item in cls._vars.items():
            if key[0] == prefix:
                d[key] = item
        return d

    @classmethod
    def restore(cls, d):
        '''
        Restore variable values from dictionary.
        '''
        for key, item in d.items():
            Variable(key, item)

    @classmethod
    def expand(cls, s):
        '''
        Expand variables in string.
        '''
        # TODO: Handle KeyError for unknown variables.
        # TODO: Better (regex/recursive?) variable expandsion.
        for x in range(0, 3):
            s = s.format(**cls.get_all())
        return s
