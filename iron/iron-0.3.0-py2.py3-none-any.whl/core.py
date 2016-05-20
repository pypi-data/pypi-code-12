import subprocess
from itertools import tee

from click import echo, secho, style
from more_itertools import consume

from .exceptions import ExternalCommandError, IronTaskError
from .runtime import verbose
from .utils import chdir


def dictmerge(*dicts, **kwargs):
    """
    Merges an arbitrary number of dicts and kwargs into a single (new) dict.
    Inputs are unaffected.

    Usage:

        >>> d1 = {'a': 1}
        >>> d2 = {'b': 2}
        >>> m = dictmerge(d1, d2, moar=3)
        >>> sorted(m.items())
        [('a', 1), ('b', 2), ('moar', 3)]

    """
    result = {}
    for d in dicts:
        result.update(d)
    result.update(kwargs)
    return result


class Task:
    def __rshift__(self, other):
        return self.pipe(other)

    def __and__(self, other):
        return CombineOutputTask(self, other)

    def log(self, message):
        if verbose == True:  # noqa
            self.info(message)

    def info(self, message):
        self._info('>>> [{}] {}'.format(self.name, message))

    def _info(self, message):
        print(message)

    @property
    def name(self):
        return self.__class__.__name__

    def pipe(self, other):
        return ChainedTask(self, other)

    def __iter__(self):
        return self.process([])

    def format_for_exception(self, cause):
        s = str(self)
        if self == cause:
            return style(s, fg='red')
        return s

    def __str__(self):
        return self.name

    def run(self):
        try:
            # Iterating over the task triggers all the behaviour
            consume(self)
        except IronTaskError as e:
            echo('Exception occurred while processing:')
            echo(self.format_for_exception(cause=e.task))
            secho(str(e), fg='red')


class ChainedTask(Task):
    def __init__(self, task1, task2):
        self.task1 = task1
        self.task2 = task2

    def process(self, inputs):
        return self.task2.process(self.task1.process(inputs))

    def __str__(self):
        return '{} >> {}'.format(self.task1, self.task2)

    def format_for_exception(self, cause):
        return ('{} >> {}'.format(self.task1.format_for_exception(cause),
                                  self.task2.format_for_exception(cause)))


class CombineOutputTask(Task):
    def __init__(self, task1, task2, **kwargs):
        super().__init__(**kwargs)
        self.task1 = task1
        self.task2 = task2

    def process(self, inputs):
        inputs1, inputs2 = [], []
        for t, c, m in inputs:
            self.log('t = {}'.format(t))
            self.log('c = {}'.format(c))
            c1, c2 = tee(c)
            inputs1.append((t, c1, dictmerge(m)))
            inputs2.append((t, c2, dictmerge(m)))

        self.log('inputs1 = {}'.format(inputs1))
        self.log('inputs2 = {}'.format(inputs2))
        yield from self.task1.process(inputs1)
        yield from self.task2.process(inputs2)

    def __str__(self):
        return '({} & {})'.format(self.task1, self.task2)

    def format_for_exception(self, cause):
        return ('({} & {})'.format(self.task1.format_for_exception(cause),
                                   self.task2.format_for_exception(cause)))


class ExternalCommandTask(Task):
    def run_external(self, cmd, *, cwd=None, input=b''):
        with chdir(cwd):
            try:
                return subprocess.check_output(cmd, input=input)
            except subprocess.CalledProcessError as e:
                raise ExternalCommandError('Error while running {}'.format(cmd),
                                           cmd=cmd,
                                           details=str(e),
                                           task=self, cwd=cwd) from e
