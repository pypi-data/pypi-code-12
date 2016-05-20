import humanize
import os
import pprint
from itertools import tee

from click import echo, secho, style
from pathlib import Path

from ..core import Task
from ..exceptions import IronError
from ..io import lazy_read, write_to_file
from ..runtime import verbose


class dump(Task):
    """
    Dumps (echoes) the contents of all streams.

    Synchronizes and buffers all stream contents before proceding, unless
    sync=False is used.
    """
    def __init__(self, sync=True):
        self.sync = sync

    def process(self, inputs):
        if self.sync:
            inputs = list(inputs)

        for t, c, m in inputs:
            c1, c2 = tee(c)
            secho(str(t), fg='magenta')
            secho(pprint.pformat(m, depth=1), fg='yellow')
            if verbose == True:  # TODO: ugh, use g.verbose  # noqa
                echo(b''.join(c1))
            yield t, c2, m


class glob(Task):
    """
    Globs from the current directory using the given pattern(s).

    Multiple patterns may be given.  If some files match multiple patterns,
    they will only be yielded once.  This property may be put to use
    conveniently for example when the order of concatenation is important for
    *some* files.  Example::

        glob('src/js/main.js',  # first output main.js
             'src/js/**/*.js'   # then everything else (main.js will not be included again)
        )

    This will even work when the pattern is specified a little different::

        # even with a different prefix, glob knows it's the same file
        glob('src/js/main.js',
             './src/js/**/*.js'
        )

    """

    def __init__(self, *patterns):
        self.patterns = patterns

    def process(self, inputs):
        root = Path('.')

        # Keep a set to filter out duplicates (matching multiple patterns)
        seen = set()
        for pattern in self.patterns:
            for t in sorted(root.glob(pattern)):
                if t not in seen and t.is_file():
                    yield t, lazy_read(t), {}
                    seen.add(t)
        if not seen:
            raise IronError('{} did not output any files'.format(self))

    def __str__(self):
        return 'glob({})'.format(', '.join(map(repr, self.patterns)))


class log(Task):
    def __init__(self, message, sync=True):
        self.message = message
        self.sync = sync

    def process(self, inputs):
        if self.sync:
            inputs = list(inputs)
        self._info(self.message)
        yield from inputs


class noop(Task):
    def process(self, inputs):
        yield from inputs


class sync(Task):
    def process(self, inputs):
        inputs = list(inputs)
        yield from inputs


class walk(Task):
    """
    Given a root directory, yields each file underneath it, recursively
    iterating over all directories.

    Example::

        >>> t = walk('src') >> dump()
        >>> t.run()
        foo.js
        bar/baz.js
        bar/qux.js
        ...

        >>> t = walk('src', relative=False) >> dump()
        >>> t.run()
        src/foo.js
        src/bar/baz.js
        src/bar/qux.js
        ...

    """
    IGNORE = {'.DS_Store'}

    def __init__(self, *roots, relative=True):
        roots = list(map(Path, roots))
        for root in roots:
            assert root.is_dir(), 'Directory not found: {}'.format(root)
        self.roots = roots
        self.relative = relative

    def _iter_recursive(self, root):
        for path in root.iterdir():
            if path.is_file() or path.is_symlink():
                if path.name not in self.IGNORE:
                    yield path
            elif path.is_dir():
                yield from self._iter_recursive(path)

    def process(self, inputs):
        for root in self.roots:
            for path in self._iter_recursive(root):
                if self.relative:
                    yield path.relative_to(root), lazy_read(path), {}
                else:
                    yield path, lazy_read(path), {}


class write(Task):
    """
    Writes inputs to the file system.

    .. note::
       Since this is typically the last task in a chain, the default
       invocation of ``write()`` does not make a copy of its inputs and will
       simply emit empty contents for each file.

       If you want to produce intermediate writes or chain it to another task,
       use ``end=False``.  This will write the files to disk and pass through
       the content streams to the next process.
    """
    CLEARED_MSG = b'Output cleared by write(). Use write(end=False) to prevent this.'

    def __init__(self, root, silent=False, end=True):
        self.silent = silent
        self.end = end
        self.root = Path(root)

    def process(self, inputs):
        dirs = set()
        for t, c, m in inputs:
            concrete_path = self.root.joinpath(t)

            dir = concrete_path.parent
            if dir not in dirs:
                dirs.add(dir)
                if not dir.exists():
                    if not self.silent:
                        self.log('mkdir {}'.format(dir))
                    dir.mkdir(parents=True)

            if self.end:
                c1, c2 = c, [self.CLEARED_MSG]
            else:
                c1, c2 = tee(c)
            write_to_file(concrete_path, c1)
            stat_info = os.stat(str(concrete_path))
            num_bytes = stat_info.st_size
            num_bytes = humanize.naturalsize(num_bytes)
            if not self.silent:
                echo(style(str(concrete_path), fg='green') + ' written (' + style(num_bytes, fg='magenta') + ')')
            else:
                self.log(str(concrete_path) + ' written (' + num_bytes + ')')
            yield t, c2, m
