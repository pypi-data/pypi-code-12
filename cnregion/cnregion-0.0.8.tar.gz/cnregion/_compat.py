# coding: utf-8
import sys


__all__ = ['PY2', 'unicode_type']


PY2 = sys.version_info[0] == 2


if PY2:
    unicode_type = lambda x: unicode(x)
else:
    unicode_type = str


class UnicodeMixin(object):
    if PY2:
        def __str__(self):
            return self.__unicode__().encode('utf8')
    else:
        def __str__(self):
            return self.__unicode__()
