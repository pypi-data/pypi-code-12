# encoding: utf8
from __future__ import absolute_import, print_function

import copy

from pyundo.task import TaskBase
from pyundo.exceptions import DoError, UndoError


class LineFlow(object):
    def __init__(self, retry=0):
        self.retry = retry
        self._tasks = []

    def add(self, task):
        """Add a task to execute."""
        if not isinstance(task, TaskBase):
            raise TypeError("Task must be the sub-class pytask.TaskBase")

        self._tasks.append(task)

    def tasks(self, index=None):
        """Get the task(s).

        If giving `index`, return the specific Nth task. Or, return the list
        of all the task.
        """
        if index:
            return self._tasks[index]
        return copy.deepcopy(self._tasks)

    def _do(self, task):
        for i in range(self.retry):
            try:
                task.do()
            except Exception as err:
                _err = err
            else:
                return

        raise DoError(_err)

    def _undo(self, task):
        count = 0
        for i in range(self.retry):
            count += 1
            try:
                task.undo()
            except Exception as err:
                _err = err
            else:
                return

        raise UndoError("Failed to undo the {0}th task: {1}".format(count, _err))

    def execute(self):
        """Execute all the tasks.

        If a certain task fails, it will undo all the tasks that have executed
        successfully.

        @Exception:
            If a task failed and undo succeeded, raise `DoError`.
            If undo failed, raise `UndoError`.
        """
        _exec_tasks = []
        count = 0
        _err = None
        for task in self._tasks:
            count += 1
            try:
                self._do(task)
            except DoError as err:
                _err = err
                break
            else:
                _exec_tasks.append(task)

        if _err:
            for task in reversed(_exec_tasks):
                self._undo(task)

            raise DoError("Failed to execute the {0}th task: {1}".format(count, _err))

    def __len__(self):
        return len(self._tasks)
