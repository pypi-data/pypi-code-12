# -*- coding: utf-8 -*-
#
# PyParadox is a nix launcher for Paradox titles.
# Copyright (C) 2014  Carmen Bianca Bakker <carmenbbakker@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import subprocess
import logging
import glob
import re

GAMES = {
    "ck2": "Crusader Kings II",
    "eu4": "Europa Universalis IV",
    "stellaris": "Stellaris",
}
# Maybe move this to a user-editable file at some point?  Hard-coding sucks.
EXPANSION_NAMES = [
    # Crusader Kings 2
    "The Sword of Islam",
    "Legacy of Rome",
    "Sunset Invasion",
    "The Republic",
    "The Old Gods",
    "Sons of Abraham",
    "Rajas of India",
    "Charlemagne",
    "Way of Life",
    "Horse Lords",
    "Conclave",
    # Europa Universalis IV
    "Conquest of Paradise",
    "Wealth of Nations",
    "Res Publica",
    "Art of War",
    "El Dorado",
    "Common Sense",
    "The Cossacks",
]

_logger = logging.getLogger(__name__)


class Plugin(object):
    """Container class that represents a single plugin (mod/DLC/expansion)."""

    MOD = 0
    DLC = 1
    EXPANSION = 2

    def __init__(self, name, file_name, plugin_type=0, enabled=True):
        """:param str name: Full name of the plugin.
        :param str file_name: Name of the plugin file.
        :param int plugin_type: Integer that determines the plugin type.
        :param bool enabled: Whether or not the plugin is currently selected
                             for use.
        """
        self.name = name
        self.file_name = file_name
        self.plugin_type = plugin_type
        self.enabled = enabled


def find_plugins(path, extension, config=None):
    """Find plugins in *path* that match *extension*.

    If *config* is provided, it will determine whether the plugins should be
    enabled or disabled on instantiation.  By default, the mods will be
    disabled and the DLCs will be enabled.

    :param str path: File system path to the directory containing the plugins.
    :param str extension: File type extension of the plugins.  Needn't begin
                          with a full stop, but it's optional.
    :keyword config: Configuration mapping that determines the *enabled* status
                     of the generated plugins.
    :type config: :class:`Config <pyparadox.config.Config>` or :class:`dict`
    :return: List of plugins.
    :rtype: [:class:`Plugin`]
    """
    extension = extension.strip(".")
    plugin_paths = glob.glob(os.path.join(path, "*.{}".format(extension)))

    plugins = []

    if config is not None:
        mods = config["mods"]
        excluded_dlcs = config["excluded_dlcs"]
    else:
        mods = []
        excluded_dlcs = []

    for path in plugin_paths:
        file_name = os.path.basename(path)
        _logger.debug("found {}".format(path))

        with open(path) as fp:
            try:
                name = find_plugin_name(fp.read())
            except ValueError:
                name = file_name

        if extension == "mod":
            plugin_type = Plugin.MOD
            enabled = file_name in mods
        elif extension == "dlc":
            plugin_type = (Plugin.EXPANSION if name in EXPANSION_NAMES else
                           Plugin.DLC)
            enabled = file_name not in excluded_dlcs
        else:
            # Assume it is a mod. This technically should never happen.
            _logger.error("{} does not have the correct file extension".format(
                path))
            plugin_type = Plugin.MOD
            enabled = file_name in mods

        plugin = Plugin(name, file_name, plugin_type=plugin_type,
                        enabled=enabled)
        plugins.append(plugin)

    return plugins


def find_plugin_name(plugin_contents):
    """Find the proper name of a plugin inside the contents of its file.

    :param str plugin_contents: The entire contents of the plugin file (or just
                                the part that contains the necessary
                                information).
    :return: Proper name of the plugin.
    :rtype: str
    :raise ValueError: If a plugin name couldn't be found.
    """
    try:
        return re.search('^name[ \t]*=[ \t]*"(.*)"', plugin_contents,
                         re.MULTILINE).group(1)
    except AttributeError as e:
        raise ValueError("Could not find plugin name",
                         plugin_contents) from e


def make_command(binary_path, mods, excluded_dlcs):
    """Compile a command that can be parsed by the :mod:`subprocess` module.

    :param str binary_path: Path (absolute) towards the executable.
    :param list mods: List of mods to be enabled.
    :param list excluded_dlcs: List of DLCs to be disabled.
    :return: Command that the :mod:`subprocess` module can process.
    :rtype: list
    """
    command = [binary_path]
    command.append("-skiplauncher")
    for mod in mods:
        command.append("-mod={}".format(os.path.join("mod", mod)))
    for dlc in excluded_dlcs:
        command.append("-exclude_dlc={}".format(os.path.join("dlc", dlc)))
    if sys.platform == "darwin":
        command.insert(1, "--args")
        command = ["open", "-n"] + command
    return command


def execute_command(command, synchronous=False):
    """Execute the command in a separate process.

    If *synchronous* is :const:`True`, the program will wait until the other
    process has finished.

    :param list command: Command to be executed.
    :param bool synchronous: Whether or not the subprocess should be
                             synchronous.
    :return: The spawned process.
    """
    _logger.debug("executing {}".format(" ".join(command)))
    if synchronous:
        return subprocess.call(command)
    else:
        return subprocess.Popen(command)
