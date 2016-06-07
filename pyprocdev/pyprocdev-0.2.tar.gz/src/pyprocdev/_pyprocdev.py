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
Pyprocdev main class.
"""
import itertools

from ._errors import ProcDevParsingError
from ._errors import ProcDevValueError

from ._constants import DeviceTypes


class _TablePairs(object):
    """
    Tables that are inverses of each other.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, left, right):
        """
        Initializer.

        :param left: table mapping x to y
        :param rigth: table mapping y to xs
        """
        self.left = left
        self.right = right


def _build_reverse_table(table):
    """
    Build a table that reverses ``table``.

    :param table: a mapping from x to y

    :returns: a table that reverses the mapping
    :rtype: dict of y * (sorted list of x)
    """
    items = sorted(table.items(), key=lambda x: x[1])
    groups = itertools.groupby(items, lambda x: x[1])
    return dict((key, sorted(x[0] for x in pairs)) for key, pairs in groups)

class ProcDev(object):
    """
    Main class for /proc/devices data.
    """

    def _parse_file(self, filepath='/proc/devices'):
        """
        Parse the file, initializing data structures.

        :param str filepath: the filepath to parse

        :raises ProcDevParsingError:
        """
        parsing = None
        with open(filepath) as istream:
            for line in istream:
                line = line.rstrip()

                if line == "":
                    parsing = None
                    continue

                if line == "Character devices:":
                    # pylint: disable=redefined-variable-type
                    parsing = DeviceTypes.CHARACTER
                    continue

                if line == "Block devices:":
                    # pylint: disable=redefined-variable-type
                    parsing = DeviceTypes.BLOCK
                    continue

                try:
                    (major, device) = line.split()
                except ValueError: # pragma: no cover
                    raise ProcDevParsingError(
                       "Unexpected format for line %s" % line
                    )

                try:
                    table = self._tables[parsing].left
                except KeyError: # pragma: no cover
                    raise ProcDevParsingError(
                       "Parsing data for unknown device type %s." % parsing
                    )

                table[int(major)] = device

    def __init__(self, filepath='/proc/devices'):
        """
        Initializer.

        :param str filespath: the filepath from which to read the data

        :raises: ProcDevError on failure
        """
        self._tables = {
           DeviceTypes.CHARACTER : _TablePairs(dict(), None),
           DeviceTypes.BLOCK : _TablePairs(dict(), None)
        }

        self._parse_file(filepath)

    def _left_table(self, device_type):
        """
        Returns the left table for ``device_type``.

        :param DeviceType device_type: the device type

        :returns: the left table
        :rtype: dict of int * str

        :raises ProcDevValueError:
        """
        try:
            table_pair = self._tables[device_type]
        except KeyError:
            raise ProcDevValueError(device_type, "device_type")
        return table_pair.left

    def _right_table(self, device_type):
        """
        Returns the right table for ``device_type``.

        :param DeviceType device_type: the device type

        :returns: the right table
        :rtype: dict of str * (set of int)

        :raises ProcDevValueError: on bad device type
        """
        try:
            table_pair = self._tables[device_type]
        except KeyError:
            raise ProcDevValueError(device_type, "device_type")

        if table_pair.right is None:
            table_pair.right = _build_reverse_table(table_pair.left)

        return table_pair.right

    def majors(self, device_type):
        """
        The major numbers for ``device_type``.

        :param DeviceType device_type: the device type

        :returns: a sorted list of major numbers
        :rtype: list of int

        :raises ProcDevValueError: on bad ``device_type``
        """
        return sorted(self._left_table(device_type).keys())

    def drivers(self, device_type):
        """
        The drivers for ``device_type``.

        :param DeviceType device_type: the device type

        :returns: the names of drivers for this device type
        :rtype: set of str

        :raises ProcDevValueError: on bad ``device_type``
        """
        return frozenset(self._right_table(device_type).keys())

    def get_driver(self, device_type, major_number):
        """
        Get the driver name for ``major_number``.

        :param DeviceType device_type: the device type
        :param int major_number: the major number

        :returns: the drive name for this major number or None if none
        :rtype: str

        :raises ProcDevValueError: for bad device type or major number
        """
        try:
            return self._left_table(device_type)[major_number]
        except KeyError:
            raise ProcDevValueError(
               major_number,
               "major_number",
               "unknown major_number %s for device_type %s" % \
                   (major_number, device_type)
            )

    def get_majors(self, device_type, driver):
        """
        Get the major numbers for ``driver``.

        :param DeviceType device_type: the device type
        :param str driver: the name of the driver

        :returns: the set of major numbers corresponding to this driver
        :rtype: sorted list of int

        :raises ProcDevValueError: for a bad device type or driver
        """
        try:
            return self._right_table(device_type)[driver]
        except KeyError:
            raise ProcDevValueError(
               driver,
               "driver",
               "unknown driver %s for device_type %s" % (driver, device_type)
            )
