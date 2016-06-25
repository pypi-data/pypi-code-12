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
import configparser
from os.path import expanduser
from typing import Dict
from tok_tokkie.modules.PluginManager import PluginManager

main_dir = os.path.join(expanduser('~'), ".toktokkie")
"""
The main directory path used for installation. It is located in the user's home directory
in a subdirectory named .toktokkie, which will show as a hidden directory in Linux.
"""

config_dir = os.path.join(main_dir, "configs")
"""
The config file directory path. This is a subdirectory of main_dir. It is designated to hold various
configuration files.
"""

main_config = os.path.join(config_dir, "mainconfig")
"""
The path to the main configuration file of the program.
"""


class Installer(object):
    """
    This Class handles the installation of the program

    The media-manager program uses a hidden config directory inside the
    user's home directory to store various files, like a file containing
    the active modules

    It is currently very bare bones and not all that necessary, but it may help
    in expanding the project further should it become more complicated in the future
    """

    @staticmethod
    def is_installed() -> bool:
        """
        Checks if the program is installed

        :return: True is it is installed, False if not
        """
        # This checks if the previously defined directories and files exist or not
        # If they all exist, the program is installed, otherwise the program
        # is not installed and has to be installed in the next step
        if not os.path.isdir(main_dir) or \
                not os.path.isdir(config_dir) or \
                not os.path.isfile(main_config):
            return False
        if not Installer.__ensure_config_file_integrity__(False):
            return False
        return True

    @staticmethod
    def install() -> None:
        """
        Installs the program in the user's home directory

        :return: None
        """
        # Checks each of the directories and files again if they exit and adds them
        # if necessary
        if not os.path.isdir(main_dir):
            os.makedirs(main_dir)
        if not os.path.isdir(config_dir):
            os.makedirs(config_dir)
        if not os.path.isfile(main_config):
            # Here, a default config file is written
            Installer.__write_main_config__()

        Installer.__ensure_config_file_integrity__(True)

    @staticmethod
    def __write_main_config__(plugin_override: Dict[str, str]=None) -> None:
        """
        Writes a default main config file
        :param plugin_override: A dictionary that can be used to customize the plugin configuration
                in the config file.
        :return: None
        """
        file = open(main_config, "w")
        # The active modules section
        file.write("[modules]\n")

        if plugin_override is None:
            for plugin in PluginManager.all_plugins:
                file.write(plugin.get_config_tag() + " = True\n")
        else:
            # noinspection PyTypeChecker
            for key in plugin_override:
                file.write(key + " = " + plugin_override[key] + "\n")

        # Here are some default things entered. Even though I believe that they
        # are not used anywhere in the program, but they at least don't break anything.
        # And they may prove useful in the future
        file.write("\n[defaults]\n")
        file.write("downloader = hexchat\n#options = (twisted|hexchat)\n")
        file.close()  # close, because that's what you should do!

    @staticmethod
    def __ensure_config_file_integrity__(write_new: bool = False) -> bool:
        """
        Checks if the config file is correctly configured. If this is not the case,
        missing modules will be added to to the file with the values 'False'

        :return: The state of the integrity of the config file
        """

        # Read the config like in the main method
        config = configparser.ConfigParser()
        config.read(main_config)
        plugin_config = dict(config.items("modules"))

        corrected_plugins = {}  # {name: bool}
        integrity = True

        for plugin in PluginManager.all_plugins:
            try:
                # Check if plugin is in file
                corrected_plugins[plugin.get_config_tag()] = plugin_config[plugin.get_config_tag()]
            except KeyError:
                # Otherwise add it to dictionary with 'False'
                corrected_plugins[plugin.get_config_tag()] = 'False'
                integrity = False

        if write_new:
            # write new, correct config file
            Installer.__write_main_config__(corrected_plugins)
            integrity = True

        return integrity
