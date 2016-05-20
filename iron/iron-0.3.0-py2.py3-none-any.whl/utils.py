"""
Helper functions for implementing Tasks more easily.
"""
import os
from shutil import rmtree
from tempfile import mkdtemp

from pathlib import Path

IRON_TMP_ROOT = '.iron-tmp'


class chdir:
    """
    Context manager to temporarily change the current directory.

    Usage::

        print(os.getcwd())  # prints /home/nvie
        with chdir('/tmp'):
            print(os.getcwd())  # prints /tmp
        print(os.getcwd())  # prints /home/nvie

    """
    def __init__(self, target):
        self._target = str(target) if target is not None else None  # supports Paths, too
        self._prev = None

    def __enter__(self):
        if self._target:
            self._prev = os.getcwd()
            os.chdir(self._target)

    def __exit__(self, *args):
        if self._target:
            os.chdir(self._prev)


def write_to_tmp_dir(inputs):
    """
    Helper function to write inputs to a temporary directory on disk.

    The files will be written to a temporary directory, where they can be
    consumed by any external process.

    Returns:
       A tuple of the form ``(tmp_dir_path, list_of_filenames)``, example::

           (PosixPath('.iron-tmp/sTu9wX3k1'),
            ['foo.js', 'bar/baz.js', 'bar/qux.js'])

    .. note::
       The temporary directory will be automatically cleaned up when all tasks
       are finished running.
    """

    from .lib import write

    dir = Path(IRON_TMP_ROOT)
    if not dir.exists():
        dir.mkdir(parents=True)

    tmp_dir = Path(mkdtemp(dir=str(dir)))
    paths = []
    for t, _, _ in write(tmp_dir, silent=True).process(inputs):
        paths.append(t)
    return tmp_dir, paths


def rm_rf(*paths):
    """
    Recursively removes the given directories or files, if they exist.

    Like running ``rm -rf <dir> [...]``
    """
    for path in paths:
        path = Path(path)
        if path.is_dir():
            rmtree(str(path), ignore_errors=True)
        elif path.is_file():
            path.unlink()
