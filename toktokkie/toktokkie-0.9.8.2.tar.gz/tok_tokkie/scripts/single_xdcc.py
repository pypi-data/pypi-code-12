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

# imports
import os
import sys
from typing import Tuple

from tok_tokkie.modules.utils.searchengines.BotMapper import BotMapper
from tok_tokkie.modules.utils.ProgressStruct import ProgressStruct
from tok_tokkie.modules.utils.downloaders.implementations.IrcLibImplementation import IrcLibImplementation


def parse_xdcc_string(xdcc_string: str) -> Tuple[str, str]:
    """
    Parses an XDCC message string of the form '/msg BOTNAME xdcc send #PACKNUMBER' for the
    bot name and pack number
    :param xdcc_string: the XDCC message string to parse
    :return: the bot name, the pack number
    """
    bot = xdcc_string.split(" ")[1]
    pack = xdcc_string.split(" ")[4].split("#")[1]
    return bot, pack


def download_pack(xdcc_bot: str, xdcc_pack: int, target_directory: str, filename_override: str) -> None:
    """
    Downloads a single XDCC pack
    :param xdcc_bot: the bot from which the pack will be downloaded from
    :param xdcc_pack: the xdcc pack to download
    :param target_directory: the target directory
    :param filename_override: the filename, if it's an empty string, the filename will stay the
            default filename.
    :return: None
    """
    filename_override = None if not filename_override else filename_override  # Turn empty string into None object
    downloader = IrcLibImplementation(BotMapper.get_server(xdcc_bot),
                                      BotMapper.get_channel(xdcc_bot),
                                      xdcc_bot,
                                      xdcc_pack,
                                      target_directory,
                                      ProgressStruct(),
                                      file_name_override=filename_override)
    downloader.start()


def check_target_directory(args_maxlength: int) -> Tuple[str, str]:
    """
    Checks the user's arguments for the target directory and file
    :param args_maxlength: the maximum length of the arguments
    :return: the directory, the filename
    """
    if len(sys.argv) == args_maxlength:
        path = sys.argv[args_maxlength - 1]
        if os.path.isdir(path):
            return path, ""
        else:
            directory = os.path.dirname(path)
            if not os.path.isdir:
                os.makedirs(directory)
            return directory, os.path.basename(path)
    else:
        return os.getcwd(), ""


def main() -> None:
    """
    Starts the script and downloads an XDCC pack on valid input
    Invalid input will display a usage message

    The script supports entering the XDCC message string in parentheses and without

    Usage: single-xdcc (")/msg botname xdcc send #pack(") destination
    :return: None
    """
    if len(sys.argv) in range(6, 8) and sys.argv[1] == "/msg":
        bot = sys.argv[2]
        pack = sys.argv[5].split("#")[1]
        destination_dir, override_filename = check_target_directory(7)
    elif len(sys.argv) in range(2, 4) and sys.argv[1].startswith("/msg"):
        bot, pack = parse_xdcc_string(sys.argv[1])
        destination_dir, override_filename = check_target_directory(3)
    else:
        print("Invalid parameters.")
        print("Usage:\n")
        print(os.path.basename(sys.argv[0]) + " /msg BOTNAME xdcc send \\#PACKNUMBER [destination_file]")
        print(os.path.basename(sys.argv[0]) + " \"/msg BOTNAME xdcc send #PACKNUMBER\" [destination_file]")
        sys.exit(1)

    download_pack(bot, int(pack), destination_dir, override_filename)
