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
from tok_tokkie.metadata import Globals
from tok_tokkie.modules.hooks.GenericHook import GenericHook
import tok_tokkie.metadata as metadata


class MainGui(Globals.selected_grid_gui_framework):
    """
    Class that implements the Main GUI of the media manager program

    It allows the user to select one of the active modules to start.

    Using the gfworks framework, the GUI can be used on different platforms,
    currently Tkinter and GTK 3.
    """

    plugins = []
    """
    A list of modules that are to be displayed on the GUI and to which the user
    should be able to switch to.
    """

    # noinspection PyTypeChecker
    def __init__(self, active_plugins: List[GenericHook]) -> None:
        """
        Constructor for the Main GUI

        It stores the active modules as list and initializes the GUI with the
        Constructor of the selected GUI framework (Either GTK3 or Tkinter) with the
        Title "Media Manager Version" appended by the version number.

        :param active_plugins: The modules to be displayed by the GUI
        :return: None
        """
        self.plugins = active_plugins
        super().__init__("Media Manager Version " + metadata.version_number)

    def lay_out(self) -> None:
        """
        Lays out the GUI by adding buttons for all modules.

        The buttons are layed out in a way that all rows and columns are filled out equally,
        with a maximum of 3 buttons per row
        :return: None
        """

        modulo_var = 3  # This variable limits the amount of buttons per row

        # Here is checked how many buttons per row can be used at maximum to
        # ensure that the rows and columns are all filled out equally.
        while len(self.plugins) % modulo_var != 0:
            modulo_var -= 1

        i = 0  # counts amount of modules already processed
        row = 0  # The current row
        column = -1  # The current column. Has to start at -1 since it gets +='ed for the first element
        # Loop that adds all plugin buttons to the GUI
        while i < len(self.plugins):

            # This clause establishes where the button will be placed
            if i % modulo_var == 0 and not i == 0:
                # Button placed at beginning of a new row
                # Will not be called for the first element
                row += 1
                column = 0
            else:
                # Button placed at the next free column
                # This is called for the first element as well.
                column += 1

            # Define a local function for the button's functionality
            # I like this more than defining a lambda, deal with it.
            def start_button_function(widget: object, plugin: GenericHook):
                """
                The method run when pressed on the plugin button

                The widget is either a Gtk Widget or a Tkinter widget.
                :param widget: the button that caused this action
                :param plugin: the plugin to which the button is assigned
                :return: None
                """
                # Check for weird cases where this method may be called but no widget called it.
                # This should never be False
                if widget is not None:
                    plugin.start_gui(self)  # Start a plugin-specific GUI

            # Generates a button and positions it using gfworks
            button = self.generate_button(self.plugins[i].get_name(), start_button_function, self.plugins[i])
            self.position_absolute(button, column, row, 1, 1)
            i += 1
