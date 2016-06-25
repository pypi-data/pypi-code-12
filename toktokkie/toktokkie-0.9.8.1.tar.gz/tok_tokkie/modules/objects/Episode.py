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

from tok_tokkie.modules.utils.fileops.FileRenamer import FileRenamer
from tok_tokkie.modules.utils.onlinedatagetters.TVDBGetter import TVDBGetter


class Episode(object):
    """
    Episode Object, containing important episode info used for renaming an episode file
    """

    episode_file = ""
    """
    Path to the actual file of the episode
    """

    episode_number = -1
    """
    The episode number of the episode
    """

    season_number = -1
    """
    The season number of the episode
    """

    show_name = ""
    """
    The show name of the show of which this episode is a part of
    """

    old_name = ""
    """
    The old/current file name of the episode
    """

    tvdb_name = ""
    """
    The episode name of this episode according to thetvdb.com
    """

    new_name = ""
    """
    The new, generated file name for this episode
    Has the form: 'Show Name - SXXEXX - tvdb_name'
    """

    def __init__(self, episode_file: str, episode_number: int, season_number: int, show_name: str) -> None:
        """
        Constructor for the Episode class, getting information about the Episode
        via the method parameters and calculating the TVDB name of the episode

        :param episode_file: the current episode file path
        :param episode_number: the episode number
        :param season_number: the season number
        :param show_name: the show name
        :return: None
        """

        # Store data about the episode in class variables
        self.episode_file = episode_file
        self.episode_number = episode_number
        self.season_number = season_number
        self.show_name = show_name
        self.old_name = os.path.basename(episode_file)

        # Generate new and tvdb names
        self.__generate_tvdb_name()

    def rename(self) -> None:
        """
        Renames the original file to the new name generated with help of thetvdb.com

        :return: None
        """
        try:
            # Rename the old file to have the new file name
            self.episode_file = FileRenamer.rename_file(self.episode_file, self.new_name)
        except FileNotFoundError:
            try:
                # If the file does not exist, try replacing spaces with underscores and try again
                underscored_episode_file = os.path.basename(self.episode_file).replace(' ', '_')
                underscored_episode_file_path = os.path.join(os.path.dirname(self.episode_file),
                                                             underscored_episode_file)
                self.episode_file = FileRenamer.rename_file(underscored_episode_file, self.new_name)
            except FileNotFoundError:
                # If it fails again, just give up
                print("Skipping renaming file " + self.episode_file + " to " + self.new_name)
                print("Please contact the developer and explain the exact circumstances leading to this.")

    def __generate_tvdb_name(self) -> None:
        """
        Generates the episode name from thetvdb.com using the tvdb_api module

        :return: None
        """
        # Generate a TVDBGetter using the available metadata
        tvdb_getter = TVDBGetter(self.show_name, self.season_number, self.episode_number)

        # get the episode name from theTVDB.com
        self.tvdb_name = tvdb_getter.find_episode_name()
        self.new_name = tvdb_getter.get_formatted_episode_name()
