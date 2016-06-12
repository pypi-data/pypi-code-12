# -*- coding: utf8 -*-
# ####################### BEGIN LICENSE BLOCK ########################
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
# 02110-1301 USA
# ######################## END LICENSE BLOCK #########################

"""
Collections of custom exceptions
"""

from __future__ import unicode_literals, print_function


class UnsupportedRotation(Exception):
    """
    Raised when unsupported rotation value is given.
    """


class MallformedResize(Exception):
    """
    Raised when resize value is mallformed
    """

class PercentageOutOfRange(Exception):
    """
    Raised when resize percentage is out of range
    """

class UnsupportedFormat(Exception):
    """
    Raised when file format is unsupported
    """


class UnkownError(Exception):
    """
    Raised when an unkown error is returned by the API
    """


class ServerError(Exception):
    """
    Raised when a Server error occured
    """


class EmptyResponse(Exception):
    """
    Raised when the server response is emtpy
    """
