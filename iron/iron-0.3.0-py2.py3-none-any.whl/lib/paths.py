from pathlib import Path

from ..core import Task


class directory(Task):
    def __init__(self, dirname):
        self.dirname = Path(dirname)

    def process(self, inputs):
        for t, c, m in inputs:
            yield self.dirname / t, c, m


class modify_path(Task):
    """Generic purpose task for changing file paths."""
    def __init__(self, func):
        self.func = func

    def process(self, inputs):
        for t, c, m in inputs:
            yield Path(self.func(t)), c, m


def rename_replace(substring, replacement):
    func = lambda path: str(path).replace(substring, replacement)
    return modify_path(func)


class relative_to(Task):
    def __init__(self, base):
        self.base = base

    def process(self, inputs):
        for t, c, m in inputs:
            try:
                t2 = t.relative_to(self.base)
            except ValueError:
                continue  # drop file
            yield t2, c, m


class strip_dirs(Task):
    """
    Flattens file names, by stripping off directory components from the files
    and keeping only the base names.

    Modifies target filenames.
    Does not modify stream contents.

    Example::

        foo.js               =>  foo.js
        foo/bar/baz/quux.js  =>  quux.js

    .. warning::
       Be aware that stripping off directory components may result in
       duplicate file names, for example ``foo/qux.js`` and ``bar/qux.js``
       both rename their target to ``qux.js``, which is fine while still
       processing the stream, but will result in undefined behaviour when
       writing the stream output to disk.
    """
    def process(self, inputs):
        for t, c, m in inputs:
            t2 = Path(t.name)
            yield t2, c, m
