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
import os
import shutil


class FileMover(object):
    """
    Class that contains static methods to help move files using convenient
    parameter options
    """

    @staticmethod
    def move_file(file: str, location: str) -> str:
        """
        Moves a file to a new location, keeping the same file name and extension

        :param location: the new location of the file (This is a file system path to a directory)
        :param file: the file to be moved (This is a file system path to a file)
        :return: the path to the move file
        """

        file_name = os.path.basename(file)  # Get the file name
        new_file = os.path.join(location, file_name)  # Generate the new file path
        print("Moving " + file_name + " to " + location)  # Print a helpful message to the console
        shutil.move(file, new_file)  # Move the file

        return new_file  # return the new file path so that the caller can process it further
