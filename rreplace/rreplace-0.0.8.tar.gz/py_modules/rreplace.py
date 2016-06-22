#!/usr/bin/env python
from public import public


def reverse(string):
    l = list(string)
    l.reverse()
    return "".join(l)


@public
def rreplace(string, old, new, count=None):
    """string right replace"""
    string = str(string)
    r = reverse(string)
    if count is None:
        count = -1
    r = r.replace(reverse(old), reverse(new), count)
    return type(string)(reverse(r))
