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
from tok_tokkie.metadata import Globals
from tok_tokkie.modules.utils.DeepIconizer import DeepIconizer


class IconizerGui(Globals.selected_grid_gui_framework):
    """
    GUI for the Iconizer plugin, that allows the election of a directory and subsequently iconizes
    that directory.
    """

    directory_entry = None
    """
    A Text Entry in which the directory path of the directory to be iconized is stored in
    """

    director_browser = None
    """
    A button that lets the user browse for a directory, which will then be inserted into the directory_entry widget
    """

    start_button = None
    """
    A button that starts the iconizing process for the entered directory
    """

    iconizer_method_combo_box = None
    """
    A Combo box from which the user can select which iconizer method he wants to use
    """

    def __init__(self, parent: Globals.selected_grid_gui_framework) -> None:
        """
        Constructor of the IconizerGui class. It calls the constructor of the active gfworks framework
        with the title "Iconizer" and hides the parent Window

        :return: None
        """
        super().__init__("Iconizer", parent, True)

    def lay_out(self) -> None:
        """
        Sets up all interface elements of the GUI and positions them in a Grid layout manager

        :return: None
        """

        self.directory_entry = self.generate_text_entry("Enter Directory here", self.iconize_start)
        self.position_absolute(self.directory_entry, 0, 0, 3, 1)

        self.director_browser = self.generate_button("Browse", self.browse_directory)
        self.position_absolute(self.director_browser, 1, 1, 1, 1)

        self.start_button = self.generate_button("Start", self.iconize_start)
        self.position_absolute(self.start_button, 3, 0, 1, 1)

        self.iconizer_method_combo_box = self.generate_string_combo_box(DeepIconizer.get_iconizer_options())
        self.position_absolute(self.iconizer_method_combo_box, 3, 1, 1, 1)

    def iconize_start(self, widget: object) -> None:
        """
        Starts the iconizing process
        :param widget: the widget that started this method
        :return void
        """
        # Used to suppress IDE warnings about unused variables
        if widget is None:
            return

        # Read the directory from the text entry and validate that it is an existing directory
        directory = self.get_string_from_text_entry(self.directory_entry)
        if not os.path.isdir(directory):
            # If it is not a valid directory, let the user know with the help of a message dialog
            self.show_message_dialog("Not a directory!", "")
            return

        # Get the selected Iconizer method
        method = self.get_string_from_current_selected_combo_box_option(self.iconizer_method_combo_box)

        # Iconize the directory
        DeepIconizer(method).iconize(directory)

        # Let the user know that the iconizing has completed
        self.show_message_dialog("Iconizing Complete!", "")

    def browse_directory(self, widget: object) -> None:
        """
        Shows a directory chooser dialog and sets the entry to the result of the browse

        :param widget: the button that called this method
        :return: None
        """
        if widget is not None:  # Suppress IDE warnings
            selected_directory = self.show_directory_chooser_dialog()  # Open directory chooser dialog
            if selected_directory:  # If a directory was selected set the text entry to that directory path
                self.set_text_entry_string(self.directory_entry, selected_directory)
