# ZCons
#
# Zimmermann's SCons wrapper
#
# Copyright (C) 2016 Stefan Zimmermann <zimmermann.code@gmail.com>
#
# ZCons is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ZCons is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with ZCons. If not, see <http://www.gnu.org/licenses/>.

"""zcons.error

ZCons exception classes.

.. moduleauthor:: Stefan Zimmermann <zimmermann.code@gmail.com>
"""
__all__ = ['ZConsError', 'ZConsResolveSConsError', 'ZConsSConsError']


class ZConsError(RuntimeError):
    """Base class for zcons exceptions.
    """


class ZConsResolveSConsError(ZConsError):
    """SCons could not be resolved on ``import zcons`` (installation failed).
    """
    def __init__(self, reason=None):
        msg = "Failed to resolve SCons installation"
        if reason is not None:
            if isinstance(reason, Exception):
                msg += " (%s: %s)" % (type(reason).__name__, reason)
            else:
                msg += " (%s)" % reason
        super(ZConsResolveSConsError, self).__init__(msg)


class ZConsSConsError(ZConsError):
    """Running SCons via :func:`zetup.scons` failed.
    """
