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
import tvdb_api
from tvdb_exceptions import tvdb_episodenotfound, tvdb_seasonnotfound, tvdb_shownotfound
from requests.exceptions import ConnectionError


class TVDBGetter(object):
    """
    Class that uses the tvdb_api to get information from thetvdb.com

    It's possile to find episode names for tv shows, as well as rename episode files
    using conventions accepted by most major media management software like
    Plex or Kodi/XBMC
    """

    tv_show = ""
    """
    The TV show to search
    """

    season = -1
    """
    The Season number to search
    """

    episode = -1
    """
    The episode number to search
    """

    def __init__(self, tv_show: str, season: int, episode: int) -> None:
        """
        Constructor for the TVDBGetter class, which stores the metadata for the
        searched episode name as local variables

        :param tv_show: the tv show's name
        :param season: the season to search
        :param episode: the episode to search
        :return: None
        """
        self.tv_show = tv_show
        self.season = season
        self.episode = episode

    def find_episode_name(self) -> str:
        """
        Finds the episode name and returns it as string

        :return: the episode name
        """
        return self.__get_episode_name__()

    def get_formatted_episode_name(self) -> str:
        """
        Finds the episode name and returns it as formatted string

        The format is: Show Name - SXXEXX - Episode Name

        :return: formatted the episode name
        """
        episode_name = self.__get_episode_name__()
        episode_string = str(self.episode)
        season_string = str(self.season)

        # Prepend leading zeroes if the numbers are smaller than 10 (less than 2 characters long)
        if len(str(episode_string)) < 2:
            episode_string = "0" + str(episode_string)
        if len(str(season_string)) < 2:
            season_string = "0" + str(season_string)

        formatted_episode = self.tv_show + " - S" + season_string + "E" + episode_string + " - " + episode_name

        return formatted_episode

    def __get_episode_name__(self) -> str:
        """
        Searches for the episode name with help of the TV Database

        :return: the episode name, or "Episode X" if an exception occurred
        """
        try:
            # Get the episode name from tvdb
            tvdb = tvdb_api.Tvdb()
            episode_info = tvdb[self.tv_show][self.season][self.episode]
            episode_name = episode_info['episodename']
        except (tvdb_episodenotfound, tvdb_seasonnotfound, tvdb_shownotfound, ConnectionError):
            # If not found, just return generic name
            episode_name = "Episode " + str(self.episode)

        # Strip away illegal characters
        illegal_characters = ['/', '\\', '?', '<', '>', ':', '*', '|', "\"", '^']
        for illegal_character in illegal_characters:
            episode_name = episode_name.replace(illegal_character, "")

        return episode_name
