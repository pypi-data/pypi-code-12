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


class WindowsIconizer(object):
    """
    Class that iconizes folders in Windows Explorer using desktop.ini files
    """

    @staticmethod
    def iconize(directory: str, icon: str) -> None:
        """
        Iconizes the provided directory using the Windows Explorer desktop.ini iconizing method
        with the given icon.

        :param directory: the directory to be iconized
        :param icon: the icon to be used
        :return: None
        """
        # Don't iconize if icon file does not exist
        if not os.path.isfile(icon + ".ico"):
            return

        print("Iconizing Directory " + directory)

        # this is the path of the desktop.ini file
        desktop_ini_file = os.path.join(directory, "desktop.ini")
        # calculate the relative path of the icon file to the directory
        relative_path = os.path.relpath(icon, directory)

        # If the file already exists, set the attributes in a way that the program can edit the file:
        # -r : Clears read-only state
        # -s : Clears the system file attribute
        # -h : Clears the hidden state
        if os.path.isfile(desktop_ini_file):
            Popen(["attrib", "-s", "-h", "-r", desktop_ini_file]).wait()

        # Write the folder icon information to the desktop.ini file, deleting all previous content of the file
        file = open(desktop_ini_file, 'w')
        file.writelines(["[.ShellClassInfo]",  # This is a shebang-like construct for Windows to know what to do
                         "IconFile=" + relative_path,  # This sets the path to the icon file
                         "IconIndex=0",  # The rest is just some metadata stuff
                         "[ViewState]",
                         "Mode=",
                         "Vid=",
                         "FolderType=Videos"])

        # Set the attributes of the desktop.ini file to hidden, system file and read-only
        Popen(["attrib", "+s", "+h", "+r", desktop_ini_file]).wait()
        # Set the directory to read-only? What on earth? Windows is weird.
        Popen(["attrib", "+r", directory]).wait()
