# -*- coding: utf-8 -*-
from __future__ import (
    division, absolute_import, print_function, unicode_literals,
)
from builtins import *                  # noqa
from future.builtins.disabled import *  # noqa

from datetime import datetime
from os.path import isfile, isdir, exists, split, join
from shutil import copy2, copytree, move


# src: path to source file or directory.
# dst: paht to dst file or directory.
def copy(src, dst):
    if isfile(src):
        copy2(src, dst)
    elif isdir(src):
        if exists(dst):
            raise RuntimeError("dst already exists: {0}".format(dst))
        copytree(src, dst)


def backup_name():
    BACKUP_PREFIX = '.cpl-backup-'
    now = datetime.now()
    return '{0}{1}'.format(
        BACKUP_PREFIX,
        now.strftime('%Y-%m-%d-%H-%M-%S'),
    )


def replace(src, dst):
    if dst.endswith('/'):
        dst = dst[-1]
    dir_path, target_name = split(dst)
    # backup.
    if exists(dst):
        move(
            dst,
            join(dir_path, backup_name()),
        )
    # copy.
    copy(src, dst)
