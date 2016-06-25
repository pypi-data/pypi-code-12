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

LICENSE:
"""

# imports
from typing import Tuple

from tok_tokkie.modules.utils.calc.FileSizeCalculator import FileSizeCalculator


class XDCCPack(object):
    """
    Class that models an XDCC Pack Object. It contains essential information about the
    pack and how to download it, as well as methods that can be called to access the information
    in a user-presentable way
    """

    filename = ""
    """
    The pack's file name
    """

    server = ""
    """
    The IRC server on which the bot that hosts this pack lives
    """

    channel = ""
    """
    The IRC channel on which the bot that hosts this pack lives
    """

    bot = ""
    """
    The bot that hosts the pack file
    """

    packnumber = -1
    """
    The pack number of the pack.
    """

    size = -1
    """
    The approximate file size of the pack in bytes
    """

    pretty_size = ""
    """
    The file size in a more human-readable format
    """

    def __init__(self, filename: str, server: str, channel: str, bot: str, packnumber: int, size: str) -> None:
        """
        Constructor of the XDCCPack class. It gets information of the pack via the arguments
        and parses them accordingly

        :param filename: the pack's file name
        :param server: the server of the pack
        :param channel: the channel of the pack
        :param bot: the bot of the pack
        :param packnumber: the pack number
        :param size: the file size
        :return: None
        """
        self.filename = filename
        self.server = server
        self.channel = channel
        self.bot = bot
        self.packnumber = packnumber
        self.size = FileSizeCalculator.get_byte_size_from_string(size)
        self.pretty_size = size

    def to_string(self) -> str:
        """
        Returns the bot information as a string
        :return: the bot information as a string
        """
        return self.filename + "  -  " + self.bot + "  -  Size:" + self.pretty_size

    def to_tuple(self) -> Tuple[str, int, str, str]:
        """
        Returns the bot information as a tuple
        :return: the bot information as a tuple
        """
        return self.bot, self.packnumber, self.pretty_size, self.filename
