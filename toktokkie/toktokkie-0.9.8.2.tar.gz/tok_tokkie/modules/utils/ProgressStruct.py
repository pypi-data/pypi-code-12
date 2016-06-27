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


class ProgressStruct(object):
    """
    A class that provides a structure for keeping track of download progress.
    """

    total = 0
    """
    The total amount of files to download
    """

    total_progress = 0
    """
    The amount of files already downloaded
    """

    single_size = 0
    """
    The size of the currently downloading file
    """

    single_progress = 0
    """
    The amount already downloaded of the currently downloading file
    """

    def __init__(self):
        """
        Creates a new ProgressStruct with initial values == 0
        """
        self.total = 0
        self.total_progress = 0
        self.single_size = 0
        self.single_progress = 0
