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
from typing import List
from tok_tokkie.modules.objects.XDCCPack import XDCCPack
from tok_tokkie.modules.utils.ProgressStruct import ProgressStruct


class GenericDownloader(object):
    """
    Class that defines interfaces for Downloaders to implement to ensure them
    being easily switchable with the help of the DownloadManager
    """

    packs = []
    """
    A list of the packs to download
    """

    progress_struct = None
    """
    A progress structure used to communicate with other threads, for example with a GUI to
    exchange information about the download progress
    """

    target_directory = ""
    """
    The target directory for the downloaded files
    """

    show_name = ""
    """
    The show name (only use when auto-renaming)
    """

    episode_number = -1
    """
    The first episode number (only use when auto-renaming)
    """

    season_number = -1
    """
    The season number (only use when auto-renaming)
    """

    auto_rename = False
    """
    This boolean is True if the program is supposed to automatically rename the downloaded files,
    but otherwise it defaults to False
    """

    # noinspection PyTypeChecker
    def __init__(self, packs: List[XDCCPack], progress_struct: ProgressStruct, target_directory: str,
                 show_name: str = "", episode_number: int = 0, season_number: int = 0) -> None:

        """
        Constructor for a Generic Downloader

        It stores the information about the packs to download as local class variables

        This constructor should be called by every Downloader using super() to avoid code
        reuse

        :param packs: a list of the packs to be downloaded
        :param progress_struct: Structure to keep track of download progress
        :param target_directory: The target download directory
        :param show_name: the show name for use with auto_rename
        :param episode_number: the (first) episode number for use with auto_rename
        :param season_number: the season number for use with auto_rename
        :return: None
        """
        # Store variables
        self.packs = packs
        self.progress_struct = progress_struct
        self.target_directory = target_directory

        # Establish if the downloader should auto rename the files
        # Only auto rename if show name, season and episode are specified
        if show_name and episode_number > 0 and season_number > 0:
            self.show_name = show_name
            self.episode_number = episode_number
            self.season_number = season_number
            self.auto_rename = True

    @staticmethod
    def get_string_identifier() -> str:
        """
        Returns a unique string identifier with which the Downloader can be addressed by
        the DownloaderManager

        :return: the string identifier of the Downloader
        """
        raise NotImplementedError()

    def download_single(self, pack: XDCCPack) -> None:
        """
        Downloads a single pack using the specific Downloader

        :param pack: The pack to download
        :return: None
        """
        raise NotImplementedError()

    # noinspection PyTypeChecker
    def download_loop(self) -> List[str]:
        """
        Downloads all files stored by the Constructor and return a list of file paths to the
        downloaded files

        :return: the list of file paths of the downloaded files
        """
        files = []  # The downloaded file paths
        self.packs.sort(key=lambda x: x.filename)  # Sorts the packs by file name

        for pack in self.packs:  # Download each pack
            files.append(self.download_single(pack))  # Download pack and append file path to files list

            # Reset the progress of the single file to 0
            self.progress_struct.single_progress = 0
            self.progress_struct.single_size = 0

            self.progress_struct.total_progress += 1  # Increment progress structure
        return files
