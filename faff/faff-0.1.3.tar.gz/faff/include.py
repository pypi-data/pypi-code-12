#!/usr/bin/env python
import os
import sys
import importlib
from .core import core
from .exceptions import (
    InvalidInputFileError,
    UnknownTargetRuleError,
)
from .rule import Rule


class Include(object):
    '''
    Include class.
    '''
    # Class error messages.
    E1 = '`{0}` is not a python module'
    E2 = 'failed to import `{0}`'
    E3 = 'unknown target rule `{0}`'

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
                self.E1.format(path),
                cls=InvalidInputFileError,
            )

        # If not empty, append directory to system path.
        if dpath != '':
            sys.path.append(dpath)

        # Try to import the module.
        try:
            mod = importlib.import_module(fname)
        except ImportError:
            # Write to stderr if module import failed.
            core.write_stderr(self.E2.format(path))
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
                cls.E3.format(target),
                cls=UnknownTargetRuleError,
            )
        else:
            return cls._rules[target]
