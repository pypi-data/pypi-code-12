# -*- coding: utf-8 -*-
import sys


def text_(s, encoding='latin-1', errors='strict'):
    """ If ``s`` is an instance of ``binary_type``, return
    ``s.decode(encoding, errors)``, otherwise return ``s``"""
    # True if we are running on Python 3.
    PY3 = sys.version_info[0] == 3
    if PY3:
        binary_type = bytes
    else:
        binary_type = str
    if isinstance(s, binary_type):
        return s.decode(encoding, errors)
    return s