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


class FileRenamer(object):
    """
    Class that contains static methods to help rename files using convenient
    method arguments
    """

    @staticmethod
    def rename_file(file: str, new_name: str) -> str:
        """
        Renames a file to a new file name, keeping the extension and file path.
        :param file: the file to be renamed
        :param new_name: the new name of the file
        """
        original_file_name = os.path.basename(file)  # Get the original file name (for calc'ing the extension)
        extension = os.path.splitext(original_file_name)[1]  # Get the file extension
        new_file = os.path.join(os.path.dirname(file), new_name + extension)  # Calculate the new file path
        print("renaming file " + file + " to " + new_name)  # Print to console what is happening
        shutil.move(file, new_file)  # Rename the file
        return new_file  # Return the new path to the file
