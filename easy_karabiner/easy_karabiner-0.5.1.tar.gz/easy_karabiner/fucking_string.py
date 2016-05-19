# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
import codecs

__all__ = ['ensure_utf8', 'u', 'write_utf8_to']


# if python 3.x
if sys.version_info[0] == 2:
    def write_utf8_to(s, outpath):
        with codecs.open(outpath, 'w', encoding='utf8') as fp:
            fp.write(s)
else:
    basestring = str
    unicode = str

    def write_utf8_to(s, outpath):
        with open(outpath, 'w') as fp:
            fp.write(s)


def is_string_type(s):
    return isinstance(s, (basestring, unicode, str))


def ensure_utf8(s):
    # convert from any object to `unicode`
    if not isinstance(s, basestring):
        s = unicode(s)

    if isinstance(s, unicode):
        s = s.encode('utf-8')
    return unicode(s, encoding='utf-8')


u = ensure_utf8
