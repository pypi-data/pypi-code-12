# encoding: utf8
from __future__ import absolute_import, print_function


class TaskBase(object):
    def do(self):
        """Do the task."""
        raise NotImplemented

    def undo(self):
        """Undo the task if 'do' failed."""
        raise NotImplemented
