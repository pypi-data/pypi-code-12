#!/usr/bin/env python
import os
import shutil
# me
from fullpath import fullpath
from public import public


@public
def rm(path):
    """os.unlink and shutil.rmtree replacement"""
    if not path:
        return
    if isinstance(path, list):
        map(rm, path)
        return
    path = fullpath(path)
    if not os.path.exists(path):
        return
    if os.path.isfile(path) or os.path.islink(path):
        os.unlink(path)
        return
    if os.path.isdir(path):
        shutil.rmtree(path)
