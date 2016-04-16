# -*- coding: utf-8 -*-
# Time-stamp: < stringutils.py (2016-02-14 11:40) >

# Copyright (C) 2009-2016 Martin Slouf <martin.slouf@sourceforge.net>
#
# This file is a part of Summer.
#
# Summer is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

"""Utility string functions that should be probably part of *Python*
stdlib.

:py:data:`EMPTY_STRING` defines an empty string (ie. "")

This module is not imported into public *summer* namespace, so you should
import it directly::

    from summer import stringutils

"""

import functools
import logging

logger = logging.getLogger(__name__)

EMPTY_STRING = ""


def has_text(obj: object, strip: bool=True) -> bool:
    """Check for text in string.

    Args:

        obj (object): object to be tested

        strip (bool): if ``True`` *obj* is stripped before checking

    Returns:

        bool: ``True`` if *obj* is string and contains some non-white
              characters; ``False`` otherwise.

    """
    test = False
    if isinstance(obj, str):
        if strip:
            test = obj.strip() != EMPTY_STRING
        else:
            test = obj != EMPTY_STRING
    return test


def to_unicode(obj: object, encoding: str) -> str:
    """Return unicode representation of an object.

    Returns:

        str: unicoce string object representation

    """
    if isinstance(obj, str):
        return obj
    return bytes(obj).decode(encoding)


def wrap(text: str, width: int) -> str:
    """A word-wrap function that preserves existing line breaks and most spaces
    in the text. Expects that existing line breaks are posix newlines
    (\\\\n).

    Taken from:
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/148061/index_txt

    Args:

        text (str): text to be wrapped

        width (int): max number of characters in single line

    Returns:

        str: wrapped original text

    """
    return functools.reduce(
        lambda line, word, width=width: '%s%s%s' %
        (line,
         ' \n'[
             (len(line) - line.rfind('\n') - 1 + len(word.split('\n', 1)[0]) >= width)],
         word),
        text.split(' ')
    )
