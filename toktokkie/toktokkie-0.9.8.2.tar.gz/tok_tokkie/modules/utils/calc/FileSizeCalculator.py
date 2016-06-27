"""
LICENSE:

Copyright 2015,2016 Hermann Krumrey

This file is part of media-manager.

    media-manager is a program that allows convenient managing of various
    local media collections, mostly focused on video.

    media-manager is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    media-manager is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with media-manager.  If not, see <http://www.gnu.org/licenses/>.

LICENSE
"""

# imports
import math


class FileSizeCalculator(object):
    """
    Class that offers methods to do calculations with file sizes

    This class is mostly used by the XDCC Search functions since they sometimes return
    file sizes that are not in bytes but in kilo or even megabytes. These are marked
    with letters, which make the conversion to bytes a bit tricky.
    """

    @staticmethod
    def get_byte_size_from_string(size_string: str) -> int:
        """
        Turns a size string into a byte integer

        It does this via checking for standard abbreviations for kilo/mega/giga etc.

        :param size_string: The size string to be converted to bytes
        :return: the amount of bytes represented by the size_string
        """
        try:
            # Convert using int(float(str)) to avoid any casting errors
            try:
                # First we check if the size is given in Bytes directly
                byte_size = int(float(size_string))
            except ValueError:
                try:
                    # Now we check if the notation 'k', 'm', or 'g' was used
                    byte_size = int(float(size_string[:-1]))
                    unit = size_string[-1:].lower()
                except ValueError:
                    # Now we check if the notation 'kb', 'mb', or 'gb' was used
                    byte_size = int(float(size_string[:-2]))
                    unit = size_string[-2:].lower()

                # Now that we know which parts of the string is the unit and which part is the
                # actual size marker, we can calculate the size in bytes
                multiplier = 1
                if unit in ["k", "kb"]:
                    multiplier = math.pow(2, 10)
                elif unit in ["m", "mb"]:
                    multiplier = math.pow(2, 20)
                elif unit in ["g", "gb"]:
                    multiplier = math.pow(2, 30)
                byte_size *= multiplier
        except ValueError:
            # If something unexpected (like '<1k') is to be parsed, we just return 1
            byte_size = 1

        return byte_size
