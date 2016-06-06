'''collection of routines to support python 2&3 code in this package'''
# std py3k stanza
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import codecs
import sys
# flake8: noqa


def iteritems(dct):
    '''return the appropriate method'''
    if sys.version_info < (3, ):
        return dct.iteritems()
    else:
        return dct.items()  # pragma: no cover


def py_ver():
    '''return the Major python version, 2 or 3'''
    return sys.version_info[0]

# Exports the proper version of StringIO
try:
    from cStringIO import StringIO
except ImportError:     # pragma: no cover
    from io import StringIO

# No old-style classes in Python3
try:
    from types import InstanceType
except ImportError:
    InstanceType = object

# pylint:disable=w0622,c0103
try:
    unicode = unicode
except NameError:
    # 'unicode' is undefined, must be Python 3
    str = str
    unicode = str
    bytes = bytes
    basestring = (str, bytes)
else:
    # 'unicode' exists, must be Python 2
    str = str
    unicode = unicode
    bytes = str
    basestring = basestring


def to_unicode(obj, encoding='utf-8'):
    """Convert to unicode if possible.

    Args:
        obj (obj): object to attempt conversion of
        encoding (str): default: utf-8

    Returns: (unicode|obj)
    """
    if isinstance(obj, basestring):
        if not isinstance(obj, unicode):
            obj = unicode(obj, encoding)
    return obj


def set_output_encoding(encoding='utf-8'):
    '''If Python has punted on output encoding, give it a nudge. (def utf-8)

    Python knows the encoding needed when piping to the terminal and
    automatically sets it. However, when piping to another program
    (i.e. | less), it is None. Which means it defaults to ascii.'''
    if sys.stdout.encoding is None:
        sys.stdout = codecs.getwriter(encoding)(sys.stdout)
        sys.stdout.encoding = encoding
    if sys.stderr.encoding is None:
        sys.stderr = codecs.getwriter(encoding)(sys.stderr)
        sys.stderr.encoding = encoding
    return
