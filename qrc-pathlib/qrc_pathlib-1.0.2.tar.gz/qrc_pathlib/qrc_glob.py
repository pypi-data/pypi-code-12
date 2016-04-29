"""
Implementation of iglob and iglob via Qt
"""

import os
import re

from qrc_pathlib import QtCore


__all__ = ['iglob']


def iglob(pathname, *, recursive=False):
    from qrc_pathlib import QrcPath

    if not pathname:
        return

    if pathname.startswith(':'):
        pathname = pathname[1:]

    dirname, basename = os.path.split(pathname)

    if not has_magic(pathname):
        if not dirname:
            if QtCore.QFileInfo(':' + pathname).exists():
                yield str(QrcPath(':').joinpath(pathname))
        else:
            if QtCore.QFileInfo(':' + pathname).isDir():
                yield str(QrcPath(':').joinpath(pathname))

        return

    if not dirname:
        if recursive and _isrecursive(basename):
            yield from glob2(dirname, basename)
        else:
            yield from glob1(dirname, basename)

        return

    dirs = iglob(dirname, recursive=recursive)

    if has_magic(basename):
        if recursive and _isrecursive(basename):
            glob_in_dir = glob2
        else:
            glob_in_dir = glob1
    else:
        glob_in_dir = glob0

    for dirname in dirs:
        for name in glob_in_dir(dirname, basename):
            yield name


def glob0(dirname, basename):
    from qrc_pathlib import QrcPath

    pathname = str(QrcPath(':').joinpath(dirname, basename))

    if not basename:
        # `os.path.split()` returns an empty basename for paths ending with a
        # directory separator.  'q*x/' should match only directories.
        if QtCore.QFileInfo(pathname).isDir():
            yield pathname
    else:
        if QtCore.QFileInfo(pathname).exists():
            yield pathname


def glob1(dirname, pattern):
    """
    Enumerate given dir_path by filtering it using pattern.

    @type dir_path: QrcPath
    """
    from qrc_pathlib import QrcPath

    if not dirname:
        dirname = ':'

    pathname = str(QrcPath(':').joinpath(dirname))

    if not QtCore.QFileInfo(pathname).isDir():
        return

    filters = QtCore.QDir.NoDotAndDotDot | QtCore.QDir.Dirs | QtCore.QDir.Files
    if _ishidden(pattern):
        filters |= QtCore.QDir.Hidden

    d = QtCore.QDirIterator(pathname, [pattern], filters)
    while d.hasNext():
        yield d.next()


def glob2(dirname, pattern):
    assert _isrecursive(pattern)
    yield dirname
    yield from _rlistdir(dirname)


def _rlistdir(dirname):
    from qrc_pathlib import QrcPath

    if not dirname:
        dirname = ':'

    pathname = str(QrcPath(':').joinpath(dirname))

    i = QtCore.QDirIterator(pathname,
                            [],
                            QtCore.QDir.NoDotAndDotDot | QtCore.QDir.Dirs | QtCore.QDir.Files | QtCore.QDir.Hidden,
                            QtCore.QDirIterator.Subdirectories)
    while i.hasNext():
        p = i.next()
        yield p


magic_check = re.compile('([*?[])')


def has_magic(s):
    return magic_check.search(s) is not None


def _ishidden(path):
    return path.startswith('.')


def _isrecursive(pattern):
    return pattern == '**'
