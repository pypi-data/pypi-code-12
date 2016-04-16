# -*- coding: utf-8 -*-
# Time-stamp: < ass.py (2016-02-14 11:39) >

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

"""Provides various pre-implemented simple tests (ie. asserts) suitable for
input argument testing.

This module is not imported into public *summer* namespace, so you should
import it directly::

    from summer import ass

"""

import logging

from .ex import ApplicationException
from .stringutils import EMPTY_STRING

logger = logging.getLogger(__name__)


class AssertException(ApplicationException):

    """Raised when some of the assertions methods in this module fails."""

    def __init__(self, message: str=None, **kwargs):
        ApplicationException.__init__(self, message, **kwargs)


def is_none(obj: object, msg: str=None, **kwargs) -> bool:
    """Args:

        obj (object): object instance to be tested

        msg (str): message in exception if test fails

        kwargs: arguments forwarded to exceptions (usually context values
                that are presented in stacktrace alongside the message.

    Returns:

        bool: ``True`` if *obj* is ``None``, ``False`` otherwise.

    """
    if obj is not None:
        raise AssertException(msg, **kwargs)


def is_not_none(obj: object, msg: str=None, **kwargs) -> bool:
    """Args:

        obj (object): object instance to be tested

        msg (str): message in exception if test fails

        kwargs: arguments forwarded to exceptions (usually context values
                that are presented in stacktrace alongside the message.

    Returns:

        bool: ``True`` if *obj* is not ``None``, ``False`` otherwise.

    """
    if obj is None:
        raise AssertException(msg, **kwargs)


def is_true(expr: bool, msg: str=None, **kwargs) -> bool:
    """Args:

        expr (bool): object instance to be tested

        msg (str): message in exception if test fails

        kwargs: arguments forwarded to exceptions (usually context values
                that are presented in stacktrace alongside the message.

    Returns:

        bool: ``True`` if *expr* is ``True``, ``False`` otherwise.

    """
    if not expr:
        raise AssertException(msg, **kwargs)


def is_false(expr: bool, msg: str=None, **kwargs) -> bool:
    """Args:

        expr (bool): object instance to be tested

        msg (str): message in exception if test fails

        kwargs: arguments forwarded to exceptions (usually context values
                that are presented in stacktrace alongside the message.

    Returns:

        bool: ``True`` if *expr* is ``False``, ``False`` otherwise.

    """
    if expr:
        raise AssertException(msg, **kwargs)


def has_text(obj: str, msg: str=None, **kwargs) -> bool:
    """Args:

        obj (str): object instance to be tested

        msg (str): message in exception if test fails

        kwargs: arguments forwarded to exceptions (usually context values
                that are presented in stacktrace alongside the message.


    Returns:

        bool: ``True`` if *obj* is ``str`` and is not empty, ``False``
        otherwise.

    """
    is_not_none(obj)
    if not isinstance(obj, str):
        raise AssertException("obj is not a string",
                              obj=obj,
                              obj_class=obj.__class__.__name__)
    if obj == EMPTY_STRING:
        raise AssertException(msg, **kwargs)
