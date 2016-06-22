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
from subprocess import Popen


class NautilusNemoIconizer(object):
    """
    Class that iconizes folders for the Nemo and/or Nautilus file browsers using gvfs-set-attribute
    """

    @staticmethod
    def iconize(directory: str, icon: str) -> None:
        """
        Iconizes the given directory using the icon provided

        :param directory: the directory to be iconized
        :param icon: the icon to be used
        :return: None
        """
        # call gvfs-set-attribute to iconize the directory, but only if the icon file exists
        if os.path.isfile(icon + ".png"):
            print("Iconizing Directory " + directory)
            Popen(["gvfs-set-attribute", "-t", "string", directory, "metadata::custom-icon", "file://" + icon + ".png"])
