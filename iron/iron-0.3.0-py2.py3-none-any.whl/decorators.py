from .registry import _command_registry
from .watchers import _watch_rules


class command:
    """
    Registers a function in the ironfile as a command.

    Adding this to a function makes the function executable by running it on
    the commandline with ``iron``::

        from iron import command

        @task('ohai')
        def greet():
            print('ohai, world!')

        @task()
        def kthxbai():
            print('kthxbai, cruel world')

    The command name will be derived from the function, unless an alternative
    name is specified.
    """
    def __init__(self, name=None):
        self.name = name

    def __call__(self, f):
        name = self.name or f.__name__
        f._iron_cmdname = name
        _command_registry[name] = f
        return f


class watch:
    """
    Registers a watch pattern.
    """
    def __init__(self, path, pattern=None):
        self.path = path
        self.pattern = pattern

    def __call__(self, f):
        path = self.path
        if isinstance(path, str):
            path = [path]
        pat = self.pattern
        if pat is None:
            pat = []
        elif isinstance(pat, str):
            pat = [pat]
        _watch_rules.add((f._iron_cmdname, tuple(path), tuple(pat)))
        return f
