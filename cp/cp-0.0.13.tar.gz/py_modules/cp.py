#!/usr/bin/env python
from distutils import dir_util
import os
import shutil
# me
from assert_exists import assert_exists
from public import public


@public
def cp(source, target, force=True):
    if isinstance(source, list):  # list
        # copy files to dir
        targets = []
        for s in source:
            t = cp(s, target, force)
            targets.append(t)
        return targets
    assert_exists(source)  # assert exists
    if not force and os.path.exists(target):
        return
    if source == target:
        return target
    if os.path.isfile(source) and os.path.isdir(target):
        # target is DIR
        target = os.path.join(target, os.path.basename(source))
    if os.path.isfile(source) or os.path.islink(source):
        if (os.path.exists(target) or os.path.lexists(target)):
            if os.path.isfile(source) != os.path.isfile(target):
                os.unlink(target)
        shutil.copy(source, target)
    if os.path.isdir(source):
        # first create dirs
        if not os.path.exists(target):
            os.makedirs(target)
        dir_util.copy_tree(source, target)
    return target
