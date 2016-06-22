#!/usr/bin/env python
# -*- coding: utf-8 -*-s
import os
from isbinaryfile import isbinaryfile
from read import read
from public import public


@public
def isshebang(l):
    """return True if line is shebang"""
    return l and l.find("#!") == 0


@public
def shebang(path):
    """return file/string shebang"""
    if not path:
        return
    path = str(path)
    if not os.path.exists(path):
        return
    if isbinaryfile(path):
        return
    content = read(path)
    lines = content.splitlines()
    if lines:
        l = lines[0]  # first line
        if isshebang(l):
            l = l.replace("#!", "", 1)
            return l.lstrip().rstrip()
