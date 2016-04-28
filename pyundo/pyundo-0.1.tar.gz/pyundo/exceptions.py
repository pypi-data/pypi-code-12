# encoding: utf8
from __future__ import absolute_import, print_function


class TaskError(Exception):
    pass


class DoError(TaskError):
    pass


class UndoError(TaskError):
    pass
