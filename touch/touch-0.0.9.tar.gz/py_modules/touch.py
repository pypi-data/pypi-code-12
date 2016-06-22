#!/usr/bin/env python
import os
# me
from fullpath import fullpath
from public import public


@public
def touch(path):
    # todo: add datetime
    if not path:
        return
    path = fullpath(path)
    if path.find("/") > 0 and not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    try:
        os.utime(path, None)
    except Exception:
        open(path, 'a').close()
