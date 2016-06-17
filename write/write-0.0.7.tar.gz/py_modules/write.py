#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
# me
from fullpath import fullpath
from isstring import isstring
from public import public


@public
def write(path, content):
    """write to file and return fullpath"""
    path = fullpath(path)
    if content is None:
        content = ""
    if isinstance(content, dict):
        content = json.dumps(content)
    if not isstring(content):
        content = str(content)
    if str(content.__class__) == "<class 'bytes'>":
        try:
            content = str(content, "utf-8")  # python3
        except TypeError:
            # TypeError: str() takes at most 1 argument (2 given)
            content = str(content)  # python2
    # if encoding:
        # content=content.encode(encoding)
    folder = os.path.dirname(path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)
    try:
        unicode()
        if isinstance(content, unicode):
            content = content.encode("utf-8")
        open(path, "w").write(content)
    except NameError:
        # NameError: name 'unicode' is not defined
        open(path, "w", encoding="utf-8").write(content)
    return path
