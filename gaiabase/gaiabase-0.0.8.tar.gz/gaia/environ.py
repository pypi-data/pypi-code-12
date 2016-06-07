# -*- coding: utf-8 -*-

import os

def get(key):
    varname = "PRJ_%s" % key.upper()
    if varname in os.environ:
        return os.environ[varname]
    else:
        return None
