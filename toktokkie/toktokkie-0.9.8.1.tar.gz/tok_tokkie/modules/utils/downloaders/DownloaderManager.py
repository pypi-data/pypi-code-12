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
from tok_tokkie.modules.utils.downloaders.HexChatPluginDownloader import HexChatPluginDownloader
from tok_tokkie.modules.utils.downloaders.GenericDownloader import GenericDownloader
from tok_tokkie.modules.utils.downloaders.IrcLibDownloader import IrcLibDownloader


class DownloaderManager(object):
    """
    A class that manages the different kind of implemented Downloaders

    It offers methods to get the correct downloader class based on a string value, offer information
    on which Downloaders are available (for different use cases as well, for example CLI or GUI mode)
    """

    cli_downloaders = [IrcLibDownloader]

    gui_downloaders = [HexChatPluginDownloader]

    all_downloaders = [IrcLibDownloader,
                       HexChatPluginDownloader]

    # noinspection PyTypeChecker
    @staticmethod
    def get_downloader_strings(mode: str = "all") -> List[str]:
        """
        Returns downloader identifiers as strings. The mode can be set as "all", if all Downloaders
        are to be returned, or "cli" or "gui" respectively.

        :param mode: A string that sets the mode of this method. It defaults to "all"
        :return: A list of downloader identifier strings
        """
        # Initialize string list
        downloader_identifiers = []

        # Check the mode
        # We use .lower() to make the input case-insensitive
        if mode.lower() == "all":
            selected_downloaders = DownloaderManager.all_downloaders
        elif mode.lower() == "cli":
            selected_downloaders = DownloaderManager.cli_downloaders
        elif mode.lower() == "gui":
            selected_downloaders = DownloaderManager.gui_downloaders
        else:
            # Invalid modes raise an Exception
            raise AttributeError("Invalid argument, only use 'all', 'gui' or 'cli'")

        for downloader in selected_downloaders:  # Iterate over all downloaders
            downloader_identifiers.append(downloader.get_string_identifier())  # Add to list
        return downloader_identifiers  # and return the string list

    @staticmethod
    def get_downloader_from_string(string_identifier) -> GenericDownloader:
        """
        Takes a string identifier and searches for a downloader matching that string

        :param string_identifier: The identifier with which the Downloader will be selected
        :return: The specified Downloader
        """
        # This will be the variable that will be returned
        found_downloader = None

        # Iterate over all downloaders
        for downloader in DownloaderManager.all_downloaders:
            # Check if the identifier matches
            if downloader.get_string_identifier() == string_identifier:
                # Check if another Downloader was already found
                if found_downloader is None:
                    # If not, set the found_downloader variable to that downloader
                    found_downloader = downloader
                else:
                    # But if there was already a match, raise an Exception, since this should not happen
                    raise AssertionError("Found more than one Downloader for unique string identifier")

        # Raise Exception when no downloader was found.
        if found_downloader is None:
            raise AssertionError("Found no Downloader for string identifier '" + string_identifier +
                                 "', was DownloadManager.get_downloader_strings() used?")
        else:
            # If everything is OK, return the Downloader
            return found_downloader
