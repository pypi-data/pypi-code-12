"""Tools to access resources on the system."""

import pathlib
import sys


class FsDirectories:
    """Fixed locations on the filesystem.

    All attributes are ``pathlib.Path`` instances.

    :prefix: The istallation prefix.
    :bindir: Directory where binaries are located.
    :sbindir: Direcotry where administrator binaries are located.
    :sysconfdir: Directory where configuration files are located.
    :statedir: Directory where applications can store state.
    :libdir: Directory where code libraries are stored.
    :datadir: Directory where read-only architecture-independed data is stored.
    :infodir: Directory where info files are stored.
    :mandir: Directory where manual pages are stored.

    """
    # These directory locations all assume this package is installed
    # in a Conda environment.  When not in a conda environment they
    # will probably be wrong.

    prefix = pathlib.Path(sys.prefix)
    bindir = prefix / 'bin'
    sbindir = prefix / 'sbin'
    sysconfdir = prefix / 'etc'
    statedir = prefix / 'var'
    libdir = prefix / 'lib'
    datadir = prefix / 'share'
    infodir = datadir / 'info'
    mandir = datadir / 'man'
