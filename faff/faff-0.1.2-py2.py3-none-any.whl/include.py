#!/usr/bin/env python
import os
import sys
import importlib
from .core import core
from .exceptions import (
    InvalidInputFileException,
    UnknownTargetRuleException,
)
from .rule import Rule


class Include(object):
    '''
    Include class.
    '''
    # Class rules dictionary.
    _rules = {}

    def __init__(self, path):
        '''
        Load decorated rule functions from a python module.
        '''
        # TODO: Relative path support.
        # Split path to get directory path, file name and extension.
        dpath, fname = os.path.split(path)
        fname, ext = os.path.splitext(fname)

        # Check the file extension is python.
        if ext != '.py':
            core.raise_exception(
                '`{0}` is not a python module'.format(path),
                cls=InvalidInputFileException,
            )

        # If not empty, append directory to system path.
        if dpath != '':
            sys.path.append(dpath)

        # Try to import the module.
        try:
            mod = importlib.import_module(fname)
        except ImportError:
            # Write to stderr if module import failed.
            core.write_stderr('failed to import `{0}`'.format(path))
        else:
            # Test module objects for rule instances.
            for name, obj in vars(mod).items():
                if Rule.is_rule(obj):
                    self._rules[name] = obj

    @classmethod
    def get_rules(cls):
        '''
        Get all imported rules as dictionary.
        '''
        return cls._rules

    @classmethod
    def get_rule(cls, target):
        '''
        Get imported rule of target.
        '''
        # Raise exception if rule of target does not exist.
        if target not in cls._rules:
            core.raise_exception(
                'unknown target rule `{0}`'.format(target),
                cls=UnknownTargetRuleException,
            )
        else:
            return cls._rules[target]
