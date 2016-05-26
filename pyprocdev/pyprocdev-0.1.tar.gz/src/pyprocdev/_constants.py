# Copyright (C) 2016 Anne Mulhern
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# the GNU General Public License v.2, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY expressed or implied, including the implied warranties of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.  You should have received a copy of the
# GNU General Public License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.  Any Red Hat trademarks that are incorporated in the
# source code or documentation are not subject to the GNU General Public
# License and may only be used or replicated with the express permission of
# Red Hat, Inc.
#
# Anne Mulhern <amulhern@redhat.com>

"""
Constants.
"""

import abc

from six import add_metaclass

@add_metaclass(abc.ABCMeta)
class DeviceType(object):
    """
    Device type super class.
    """
    # pylint: disable=too-few-public-methods
    pass

class Character(DeviceType):
    """
    Type of Character devices.
    """
    # pylint: disable=too-few-public-methods

    def __str__(self):
        return "char"

Character = Character()

class Block(DeviceType):
    """
    Type of block devices.
    """
    # pylint: disable=too-few-public-methods

    def __str__(self):
        return "block"

Block = Block()

class DeviceTypes(object):
    """
    Class of device types.
    """
    # pylint: disable=too-few-public-methods

    BLOCK = Block
    CHARACTER = Character

    @classmethod
    def types(cls):
        """
        Returns all members types.

        :returns: iterable of member types
        """
        return (cls.BLOCK, cls.CHARACTER)
