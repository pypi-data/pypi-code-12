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
from typing import Dict, List
from tok_tokkie.modules.hooks.RenamerHook import RenamerHook
from tok_tokkie.modules.hooks.IconizerHook import IconizerHook
from tok_tokkie.modules.hooks.BatchDownloadManagerHook import BatchDownloadManagerHook
from tok_tokkie.modules.hooks.ShowManagerHook import ShowManagerHook
from tok_tokkie.modules.hooks.GenericHook import GenericHook


class PluginManager(object):
    """
    Class that manages modules and checks which modules to run using the config
    Files stored in the user's home directory
    """

    all_plugins = [RenamerHook(),
                   IconizerHook(),
                   BatchDownloadManagerHook(),
                   ShowManagerHook(),
                   # new modules here
                   ]
    """
    A list of all modules contained inside the project. This list needs to be manually
    updated whenever a new plugin is added to the project.
    """

    active_plugins = []
    """
    A list of modules that are active according to the configuration file
    """

    def __init__(self, config: Dict[str, str]) -> None:
        """
        Constructor of the PluginManager class

        It gets a ConfigParser-generated config dictionary of the form {'tag': 'boolean-value'}
        passed as argument by the main method of the main project module

        The config dictionary contains the entries in the config file's [plugin] section

        It establishes which Plugins are to be marked as active according to the configuration file.

        :param config: the config file's [plugin] section as a dictionary
        """
        for plugin in self.all_plugins:
            # Check if value is set to true or equivalent
            if config[plugin.get_config_tag()].lower() in ["true", "yes", "1"]:
                # If yes, add to active modules list
                self.active_plugins.append(plugin)

    # noinspection PyTypeChecker
    def get_plugins(self) -> List[GenericHook]:
        """
        Returns a list of modules of active modules, which can then be used
        by the user interfaces. (CLI or GUI)
        :return: the list of modules
        """
        return self.active_plugins
