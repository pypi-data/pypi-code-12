#!/usr/bin/env python3
# vim: set fenc=utf8 ts=4 sw=4 et :
from .conf import Conf

def boolify(string):
    if string == 'True':
        return True
    if string == 'False':
        return False
    raise ValueError('Not a bool')

# Try to convert variables into datatypes
def autoconvert(string):
    for fn in (boolify, int, float):
        try:
            return fn(string)
        except ValueError:
            pass
    return string
