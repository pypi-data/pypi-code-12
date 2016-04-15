# -*- coding: utf-8 -*-

# --------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2016 Jonathan Labéjof <jonathan.labejof@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# --------------------------------------------------------------------

"""Middleware class module.

This module provides class tools in order to ease the development of middleware.
"""

__all__ = ['Middleware']

from .core import register

from six import add_metaclass


class _MetaMiddleware(type):
    """Handle middleware definition."""

    def __init__(cls, name, bases, attrs):

        super(_MetaMiddleware, cls).__init__(name, bases, attrs)

        register(protocols=cls.protocols(), middleware=cls)


@add_metaclass(_MetaMiddleware)
class Middleware(object):
    """Class to use such as a super class in order to automatically register it
    to specific protocols.

    This class is instanciated with uri parameters."""

    __protocols__ = []  #: protocol registration definition.

    @classmethod
    def protocols(cls):
        """Get all class protocols.

        :rtype: set"""

        baseclasses = cls.mro()

        result = set()

        for baseclass in baseclasses:
            if hasattr(baseclass, '__protocols__'):
                result |= set(baseclass.__protocols__)

            else:
                break

        return result
