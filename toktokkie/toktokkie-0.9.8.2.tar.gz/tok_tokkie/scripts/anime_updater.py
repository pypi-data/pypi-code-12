#!/usr/bin/python3
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

# /msg CR-HOLLAND|NEW xdcc send #5024
# [HorribleSubs] Flying Witch - 04 [480p].mkv
# [SUBGROUP] SHOWNAME - EPISODE [QUALITY].mkv

# imports
import os
import time
from typing import Dict, List
from tok_tokkie.modules.objects.XDCCPack import XDCCPack
from tok_tokkie.modules.utils.ProgressStruct import ProgressStruct
from tok_tokkie.modules.utils.downloaders.IrcLibDownloader import IrcLibDownloader
from tok_tokkie.modules.utils.searchengines.HorribleSubsGetter import HorribleSubsGetter


def update(config: List[Dict[str, str]]) -> None:
    """
    Updates all shows defined in the config.

    :param config: List of dictionaries with the following attributes:
                        (target directory, season, quality, horriblesubs-name, bot)
    :return: None
    """
    for show in config:

        horriblesubs_name = show["horriblesubs_name"]
        quality = show["quality"]
        season = int(show["season"])
        bot = show["bot"]

        show_directory = show["target_directory"]
        target_directory = os.path.join(show_directory, "Season " + str(season))
        meta_directory = os.path.join(show_directory, ".icons")
        showname = os.path.basename(os.path.dirname(meta_directory))

        if not os.path.isdir(meta_directory):
            os.makedirs(meta_directory)
        if not os.path.isdir(target_directory):
            os.makedirs(target_directory)

        while True:  # == Do While Loop
            current_episode = len(os.listdir(target_directory)) + 1
            next_pack = get_next(horriblesubs_name, bot, quality, current_episode)
            if next_pack:
                prog = ProgressStruct()
                downloader = IrcLibDownloader([next_pack], prog, target_directory, showname, current_episode, season)
                downloader.download_loop()
            else:
                break


def get_next(horriblesubs_name: str, bot: str, quality: str, episode: int) -> XDCCPack or None:
    """
    Gets the next XDCC Pack of a show, if there is one

    :param horriblesubs_name: the horriblesubs name of the show
    :param bot: the bot from which the show should be downloaded
    :param quality: the quality the show is supposed to be in
    :param episode: the episode to download
    :return: The XDCC Pack to download or None if no pack was found
    """

    episode_string = str(episode) if episode >= 10 else "0" + str(episode)
    wanted_episode = horriblesubs_name + " - " + episode_string + " [" + quality + "].mkv"

    searcher = HorribleSubsGetter(horriblesubs_name + " " + episode_string + " " + quality)
    results = searcher.search()

    for result in results:
        if result.bot == bot and result.filename.split("] ", 1)[1] == wanted_episode:
            return result
    return False


def start(config: List[Dict[str, str]], continuous: bool = False, looptime: int = 3600) -> None:
    """
    Starts the updater either once or in a continuous mode
    :param config: the config to be used to determine which shows to update
    :param continuous: flag to set continuous mode
    :param looptime: Can be set to determine the intervals between updates
    :return: None
    """

    if continuous:
        while True:
            update(config)
            time.sleep(looptime)
    else:
        update(config)
