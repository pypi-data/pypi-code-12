#!/usr/bin/env python
import os
import time
from .variable import Variable


class Target(object):
    '''
    Base target class.
    '''
    def out_of_date(self, other=None):
        # Compare updated times to test if target requires update.
        upd = self.updated()
        if other:
            return upd < other.updated()
        elif upd == 0:
            return True
        else:
            return False

    def updated(self):
        '''
        Get the time when target was last updated.
        '''
        return 0

    @classmethod
    def set_variables(cls, target, depends):
        '''
        Set target and dependency variables.
        '''
        # Current target string.
        Variable('_T', str(target))
        # Current dependencies list.
        if depends is not None:
            Variable('_D', ' '.join([str(x) for x in depends]))


class RuleTarget(Target):
    '''
    Rule target class.
    '''
    def __init__(self, rule):
        # TODO: Test rule argument instance.
        self._rule = rule

    def __str__(self):
        # Return concatenated target strings.
        return ' '.join([str(t) for t in self._rule.get_targets()])

    def updated(self):
        '''
        Get the current time if rule returns updated targets.
        '''
        upd, total = self._rule()
        if total > 0:
            return time.time()
        return super(RuleTarget, self).updated()


class FileTarget(Target):
    '''
    File target class.
    '''
    def __init__(self, *args, **kwargs):
        # Store positional arguments internally as list for file path.
        self._path = list(args)

        # File extension replacement option.
        self._ext = kwargs.get('ext', None)
        self._ext_orig = None

        # Optional keyword arguments.
        self._args = kwargs.get('args', None)

    def __str__(self):
        # If file extension specified, attempt to apply.
        # TODO: Check how safe this is.
        if self._ext is not None:
            pre, ext = os.path.splitext(self._path[-1])
            if self._ext_orig is None:
                self._ext_orig = ext
            self._path[-1] = pre + self._ext

        # Apply variables to arguments when evaluated as string.
        self._path = [(Variable.expand(arg)) for arg in self._path]
        return os.path.join(*self._path)

    def updated(self):
        '''
        Get the time when target file was last modified.
        '''
        # TODO: Better OSError handling.
        try:
            return os.path.getmtime(str(self))
        except OSError:
            # Ensure any parent directories exist.
            try:
                os.makedirs(os.path.dirname(str(self)))
            except OSError:
                pass

            return super(FileTarget, self).updated()

    def get_dirname(self):
        '''
        Get directory path of target file.
        '''
        return os.path.dirname(str(self))

    def get_extension(self, original=False):
        '''
        Get file extension of target file.
        '''
        if original:
            return self._ext_orig
        else:
            return self._ext

    def get_arguments(self):
        '''
        Get optional target arguments.
        '''
        return self._args
