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


class BotMapper(object):
    """
    Class that offers methods to map an XDCC bot to an IRC server and/or IRC channel
    """

    @staticmethod
    def get_server(xdcc_bot: str) -> str:
        """
        Determines the IRC Server for the bot

        :param xdcc_bot: the bot for which the server is wanted
        :return: the server for the specified bot
        """
        str(xdcc_bot)
        return "irc.rizon.net"

    @staticmethod
    def get_channel(xdcc_bot: str) -> str:
        """
        Determines the IRC channel for the bot

        :param xdcc_bot: the bot for which the channel is wanted
        :return: the channel for the specified bot
        """
        if xdcc_bot == "HelloKitty" or "CR-" in xdcc_bot:
            return "#horriblesubs"
        elif xdcc_bot == "E-D|Mashiro":
            return "#exiled-destiny"
        elif "doki" in xdcc_bot:
            return "#doki"
        else:
            return "#intel"
