# -*- coding: utf-8 -*-
# Time-stamp: < ex.py (2016-02-14 02:14) >

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
"""Exception classes used in *summer* framework.  Some are suitable for
inheritance.

"""


import sys


class ApplicationException(Exception):

    """Base class for exceptions.  Suited for custom subclassing."""

    def __init__(self, message: str=None, **kwargs):
        """Creates :py:class:`ApplicationException` instance.

        Args:

            message (str): message to be printed

            kwargs: keyword arguments are printed as are, suitable for
                    providing some context (current values of important
                    variables and such.

        """
        Exception.__init__(self)
        self.message = message
        self.kwargs = kwargs

    def __str__(self):
        tmp = "%s" % (self.__class__.__name__,)
        if self.message is None:
            pass
        else:
            tmp += " -- %s" % (self.message,)
        if len(self.kwargs) == 0:
            pass
        else:
            tmp += " -- %s" % (self.kwargs,)
        return tmp

#
# generic exceptions for common purposes #
#


class AbstractMethodException(ApplicationException):

    def __init__(self, message: str=None, **kwargs):
        ApplicationException.__init__(self, message, **kwargs)


class UnsupportedMethodException(ApplicationException):

    def __init__(self, message: str=None, **kwargs):
        ApplicationException.__init__(self, message, **kwargs)


class NotImplementedException(ApplicationException):

    def __init__(self, message: str=None, **kwargs):
        ApplicationException.__init__(self, message, **kwargs)


class UnknownAttributeException(ApplicationException):

    def __init__(self, message: str=None, **kwargs):
        ApplicationException.__init__(self, message, **kwargs)


class IllegalArgumentException(ApplicationException):

    def __init__(self, message: str=None, **kwargs):
        ApplicationException.__init__(self, message, **kwargs)


class ResourceNotFoundException(ApplicationException):

    def __init__(self, message: str=None, **kwargs):
        ApplicationException.__init__(self, message, **kwargs)

#
# summer exception hierarchy #
#


class SummerException(ApplicationException):

    """Base summer framework exception."""

    def __init__(self, message: str=None, **kwargs):
        ApplicationException.__init__(self, message, **kwargs)


class SummerConfigurationException(SummerException):

    """Raised when summer configuration is broken."""

    def __init__(self, message: str=None, **kwargs):
        SummerException.__init__(self, message, **kwargs)


class NoObjectFoundException(SummerException):

    """Raised when required object is not found in context."""

    def __init__(self, message: str=None, **kwargs):
        SummerException.__init__(self, message, **kwargs)


def exception_to_str():
    """Convert exception to stack trace.  Uses thread safe ``sys.exc_info()``.

    Return:

        str: the formatted unicode string containing the last exception
             info.

    """
    (exc_type, exc_value, exc_trace) = sys.exc_info()
    tmp = "%s: %s\n" % (exc_type.__name__, exc_value)
    try:
        current = exc_trace
        while current is not None:
            frame = current.tb_frame
            lineno = current.tb_lineno
            code = frame.f_code
            function_name = code.co_name
            filename = code.co_filename
            tmp += "    %s:%d:%s\n" % (filename, lineno, function_name)
            current = current.tb_next
    finally:
        del exc_type, exc_value, exc_trace
    return tmp[:-1]
