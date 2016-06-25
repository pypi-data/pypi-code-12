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
import configparser
import os
import sys
from os.path import expanduser
from typing import List
from gfworks.templates.generators.GridTemplateGenerator import GridTemplateGenerator

# This import construct enables the program to be run when installed via
# setuptools as well as portable
from tok_tokkie.metadata import Globals
from tok_tokkie.modules.eastereggs.EasterEggManager import EasterEggManager


# noinspection PyTypeChecker
def main(ui_override: str = "", easter_egg_override: List[str] = None) -> None:
    """
    Main method that runs the program.

    It can be used without parameters, in which case it will start in interactive
    command line mode.

    Other options include using the --gtk or --tk flags to start either a GTK 3- or
    a Tkinter-based graphical user interface. This can also be accomplished by
    passing 'gtk' or 'tk' as the ui_override parameter of the main method.

    Furthermore, the program can be used as a pure non-interactive application.
    The options that are available if used like this can be viewed using the
    --help flag.

    :param ui_override: Can override the program mode programmatically
    :param easter_egg_override: Can give a second kind of sys.argv for use in easter eggs
    :return: None
    """

    # Activate Easter Eggs
    EasterEggManager.activate_easter_eggs(sys.argv, easter_egg_override)

    # First, the used mode of the program is determined using sys.argv
    cli_mode = False

    # Try to set a GUI framework, if it fails use the CLI instead
    try:
        selected_gui = ui_override
        if not selected_gui:
            selected_gui = sys.argv[1]
        Globals.selected_grid_gui_framework = GridTemplateGenerator.get_grid_templates()[selected_gui]
    except (KeyError, IndexError):
        cli_mode = True

    # This import has to happen at this point, since the graphical frameworks from
    # gfworks have not been defined correctly in the Globals class before this.
    from tok_tokkie.modules.PluginManager import PluginManager
    from tok_tokkie.modules.gui.MainGui import MainGui
    from tok_tokkie.modules.cli.MainCli import MainCli
    from tok_tokkie.startup.Installer import Installer

    # This checks if the program is already correctly installed in the user's
    # home directory, if this is not the case the program will be installed now.
    if not Installer.is_installed():
        Installer.install()

    # This parses the config file located in the user's home directory to establish
    # which modules should be run.
    config = configparser.ConfigParser()
    config.read(os.path.join(expanduser('~'), ".mediamanager", "configs", "mainconfig"))
    plugin_config = dict(config.items("modules"))
    active_plugins = PluginManager(plugin_config).get_plugins()

    # The program starts here, using the selected mode
    if cli_mode:
        MainCli(active_plugins).start()
    else:
        gui = MainGui(active_plugins)
        gui.start()

# This executes the main method
if __name__ == '__main__':
    # Keyboard Interrupts are caught and display a farewell message when they occur.
    try:
        main()
    except KeyboardInterrupt:
        print("\nThanks for using the tok tokkie media manager!")
        sys.exit(0)
