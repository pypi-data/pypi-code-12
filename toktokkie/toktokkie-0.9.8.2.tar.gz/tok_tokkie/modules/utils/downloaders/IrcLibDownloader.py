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

# Imports
from typing import List

from tok_tokkie.modules.utils.onlinedatagetters.TVDBGetter import TVDBGetter
from tok_tokkie.modules.objects.XDCCPack import XDCCPack
from tok_tokkie.modules.utils.ProgressStruct import ProgressStruct
from tok_tokkie.modules.utils.downloaders.GenericDownloader import GenericDownloader
from tok_tokkie.modules.utils.downloaders.implementations.IrcLibImplementation import IrcLibImplementation


class IrcLibDownloader(GenericDownloader):
    """
    XDCC Downloader that makes use of irclib to connect to IRC servers and request XDCC file
    transfers

    This Downloader requires only the irclib library, which means this is the most native downloader
    implemented in media-manager
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
        Constructor for the IrcLibDownloader. It calls the constructor for the
        GenericDownloader class

        :param packs: the packs to be downloaded
        :param progress_struct: Structure that keeps track of download progress
        :param target_directory: The target download directory
        :param show_name: the show name for auto renaming
        :param episode_number: the (starting) episode number for auto renaming
        :param season_number: the season number for auto renaming
        :return: None
        """
        # Store variables
        super().__init__(packs, progress_struct, target_directory, show_name, episode_number, season_number)

    def download_single(self, pack: XDCCPack) -> str:
        """
        Downloads a single pack with the help of the irclib library
        and also auto-renames the resulting file if auto-rename is enabled

        :param pack: the pack to download
        :return: The file path to the downloaded file
        """
        # Print informational string, which file is being downloaded
        print("Downloading pack: " + pack.to_string())

        if self.auto_rename:
            # Get the auto-renamed file name
            file_name = TVDBGetter(self.show_name, self.season_number, self.episode_number).get_formatted_episode_name()
            self.episode_number += 1
        else:
            file_name = None

        downloader = IrcLibImplementation(pack.server,
                                          pack.channel,
                                          pack.bot,
                                          pack.packnumber,
                                          self.target_directory,
                                          self.progress_struct,
                                          file_name_override=file_name)
        return downloader.start()

    @staticmethod
    def get_string_identifier() -> str:
        """
        Returns a unique string identifier with which the Downloader can be addressed by
        the DownloaderManager

        :return: the string identifier of the Downloader
        """
        return "IRC Downloader"
