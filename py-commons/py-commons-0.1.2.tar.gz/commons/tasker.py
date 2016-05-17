from __future__ import print_function
from six import reraise
import sys

__doc__ = """
This module provides some support for tasks execution and dependencies.
TODO: usage and example
"""


class DependencyLoop(RuntimeError):
    pass


class Task(object):
    STATUS_CREATED = 0
    STATUS_WAIT = 1
    STATUS_RUN = 2
    STATUS_DONE = 3
    STATUS_FAILED = 4

    def __call__(self):
        return self._execute()

    def _execute(self):
        raise NotImplementedError()


class RunnableTask(Task):

    def __init__(self, call, depends_on=None):
        self.status = self.STATUS_CREATED
        self.depends_on = depends_on if depends_on else {}
        self.call = call
        self.result = None
        self.error = None
        assert self.call is not None, 'call should be provided'
        assert isinstance(self.depends_on, dict), 'depends_on should be a dict, but was {}'.format(depends_on)
        for v in self.depends_on.values():
            assert isinstance(v, Task), 'can only depend on task, but {} is not task'.format(v)

    def _execute(self):
        if self.status == self.STATUS_DONE:
            return self.result
        if self.status == self.STATUS_FAILED:
            raise RuntimeError(self.error)
        if self.status in {self.STATUS_WAIT, self.STATUS_RUN}:
            raise DependencyLoop('Loop detected')
        self.status = self.STATUS_WAIT
        try:
            arguments = {}
            for key, task in self.depends_on.items():
                arguments[key] = task()
            self.status = self.STATUS_RUN
            self.result = self._make_call(arguments)
            self.status = self.STATUS_DONE
            return self.result
        except BaseException as ex:
            self.error = ex
            self.status = self.STATUS_FAILED
            reraise(*sys.exc_info())

    def _make_call(self, arguments):
        return self.call(**arguments)


class ValueHolder(Task):
    """
    Task-like object for holding some value
    """

    def __init__(self, value):
        super(ValueHolder, self).__init__()
        self.result = value
        self.status = self.STATUS_DONE

    def _execute(self):
        return self.result


class SplitApplyCombineTask(RunnableTask):
    """
    Runnable task that splits its only argument by a given key and performs its call on the grouped values.
    Returns the concatenation of the results
    """

    def __init__(self, call, split_key, depends_on=None, n_jobs=1):
        super(SplitApplyCombineTask, self).__init__(call, depends_on)
        self.n_jobs = n_jobs
        self.split_key = split_key
        assert self.call is not None, 'call should be provided'
        assert len(self.depends_on) == 1, 'Only one dependency is currently supported'

    def _make_call(self, arguments):
        import pandas as pd
        from joblib import Parallel, delayed

        arg_name, arg_value = next(arguments.items().__iter__())
        assert isinstance(arg_value, pd.DataFrame), 'Only data frames are currently supported as the arguments'
        import pickle

        pickle.dumps(self.call)

        return pd.concat(Parallel(n_jobs=self.n_jobs, verbose=11)(
            delayed(self.call)(**{arg_name: group})
            for _, group in arg_value.groupby(self.split_key, as_index=False)
        ))
