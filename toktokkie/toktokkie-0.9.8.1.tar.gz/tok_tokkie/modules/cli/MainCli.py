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
from tok_tokkie.modules.cli.GenericCli import GenericCli
from tok_tokkie.modules.hooks.GenericHook import GenericHook


class MainCli(GenericCli):
    """
    Class that implements the Main CLI for the media manager program

    It prints the current version of the program to the console, then lists
    all the available modules, then prints an instructional string to the console
    and waits for user input.

    A plugin is selected by entering the index number displayed to the left of the
    plugin name.
    """

    plugin_dict = {}
    """
    A dictionary that maps index numbers to modules
    """

    plugin_list_string = ""
    """
    The modules displayed together with their indices as a newline-separated string
    They are sorted via their indices in ascending order
    """

    # noinspection PyTypeChecker
    def __init__(self, active_plugins: List[GenericHook]) -> None:
        """
        Constructor of the Main CLI

        It invokes the GenericCli's init Constructor  without specifying
        a parent, as this is the top-level CLI of the program.

        It also stores the list of active modules given via parameter as a
        local variable.

        These modules are then parsed and added to the plugin_dict and plugin_list
        accordingly.

        :param active_plugins: The modules to be displayed
        :return: None
        """
        super().__init__()

        # Parse the modules
        i = 1  # index number counter
        for plugin in active_plugins:
            # This is the name of the plugin + the index number, prepended by a tab character and appended by newline
            self.plugin_list_string += "\t" + str(i) + ". " + plugin.get_name() + "\n"
            # stores the plugin into the dictionary with the tag being the index number
            self.plugin_dict[i] = plugin
            i += 1  # increment the index number

    def start(self, title: str = None) -> None:
        """
        Starts the CLI by invoking the GenericCli's start method with a title,
        which prints the name of the program and the current version number as well as
        "Available Plugins:" and all active modules (the strings from plugin_list)

        :return: None
        """
        # Generates the Greeting/Title Message
        greeting_message = "TOK TOKKIE MEDIA MANAGER VERSION " +\
                           metadata.version_number +\
                           "\n\n" + "Available Modules:\n" +\
                           self.plugin_list_string

        super().start(greeting_message)

    def mainloop(self) -> None:
        """
        The main looping method of the CLI. This will be repeated until the user
        either quits the program or starts one of the modules

        It asks the user for input and allows him/her to start a plugin,
        quit the program or list all available modules once more

        :return: None
        """
        # Prints an empty string to create a sperator between loops
        print()

        # Asks the user for input
        user_input = self.ask_user("\nSelect plugin by entering the plugin index number."
                                   "\nTo exit, enter 'exit' or 'quit'"
                                   "\nTo get the list of modules again, enter 'list'\n")
        try:
            print()  # empty line
            self.plugin_dict[int(user_input)].start_cli(self)  # Try to start the plugin
            # This leads to KeyErrors if an invalid key is entered, say 100 if there are only 5 modules
            # ValueErrors can occur when the user doesn't enter a string that can be parsed as an integer
            return
        except (KeyError, ValueError):  # If starting the plugin fails, parse the user input further
            if user_input.lower() == "list":
                print(self.plugin_list_string)
                # This lists all plugin options once more
            else:
                print("Unrecognized Command")
                # If all fails, give the user this message
