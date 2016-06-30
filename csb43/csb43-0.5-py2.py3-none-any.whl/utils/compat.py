# -*- coding: utf-8 -*-
'''
.. note::

    license: GNU Lesser General Public License v3.0 (see LICENSE)
'''

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import

import sys


# python3 helpers
#-----------------
IS_PY2 = int(sys.version[0:1]) < 3

m3_unicode = unicode if IS_PY2 else str
m3_bytes = str if IS_PY2 else bytes
m3_long = long if IS_PY2 else int

if IS_PY2:
    def m3_next(obj):
        return obj.next()

    def m3_is_string(x):
        return isinstance(x, basestring)

    def m3_enc(x, fd):
        if fd.isatty():
            return x
        else:
            return x.encode('utf-8')
else:
    def m3_next(obj):
        return next(obj)

    def m3_is_string(x):
        return isinstance(x, (str, bytes))

    def m3_enc(x, fd):
        return x
