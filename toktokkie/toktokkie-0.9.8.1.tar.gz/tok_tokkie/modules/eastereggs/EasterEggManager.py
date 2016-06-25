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

import tok_tokkie.metadata as metadata
from tok_tokkie.modules.eastereggs.LeetPrint import LeetPrint


class EasterEggManager(object):
    """
    Class that manages easter eggs in the program
    """

    # noinspection PyTypeChecker
    @staticmethod
    def activate_easter_eggs(sysargs: List[str], program_args: List[str]):
        """
        Method that activates various easter eggs depending on specific metadata like the version number
        or a sys.argv argument
        :param sysargs: sys.argv from the caller
        :param program_args: arguments given programmatically
        :return: None
        """
        # Check if the given program_args are not None
        if program_args is not None:
            prog_args = program_args
        else:
            prog_args = []

        if LeetPrint is not None:
            # Activate leet speak if the version number contains the phrase 1337 or if the user gave the
            # arguments --1337 or --leet or 'leet'/'1337' programmatically
            if "1337" in metadata.version_number\
                    or "--1337" in sysargs \
                    or "--leet" in sysargs\
                    or "1337" in prog_args\
                    or "leet" in prog_args:
                LeetPrint.activate_leet(True)
