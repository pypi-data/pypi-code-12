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
from typing import List, Dict
from tok_tokkie.modules.utils.Renamer import Renamer
from tok_tokkie.metadata import Globals


class RenamerGui(Globals.selected_grid_gui_framework):
    """
    GUI for the Renamer plugin that allows the user to select a directory to rename the contents of
    """

    button = None
    """
    A button that starts the renaming of the currently entered directory
    """

    entry = None
    """
    A Text Entry that contains the path to the directory to be renamed
    """

    browse = None
    """
    A button that lets the user browse for a directory using a directory chooser dialog
    """

    def __init__(self, parent: Globals.selected_grid_gui_framework) -> None:
        """
        Constructor of the RenamerGui class. It calls the selected gfworks framework's constructor and
        hides the parent window

        :param parent: the parent gui window
        :return: None
        """
        super().__init__("Renamer", parent, True)

    def lay_out(self) -> None:
        """
        Sets up all interface elements of the GUI and positions them in a grid layout

        :return: None
        """
        # Generate the button
        self.button = self.generate_button("Start", self.start_rename)
        self.position_absolute(self.button, 4, 0, 1, 1)

        # Generate the browse button
        self.browse = self.generate_button("Browse", self.browse_directory)
        self.position_absolute(self.browse, 0, 0, 1, 1)

        # Generate the Text Entry
        self.entry = self.generate_text_entry("", self.start_rename)
        self.position_absolute(self.entry, 1, 0, 2, 1)

    def start_rename(self, widget: object) -> None:
        """
        Starts the renaming process.

        During this time, the user is asked to confirm his selection

        :param widget: the button that started this method
        :return: None
        """
        # DO this to avoid IDE warnings about unused variables
        if widget is None:
            return

        # Get the currently entered directory path
        abs_dir = self.get_string_from_text_entry(self.entry)

        # Check if the path is a valid directory
        if not os.path.isdir(abs_dir):
            self.show_message_dialog("Error, ", "Not a valid directory")
            return

        renamer = Renamer(abs_dir)  # Create a new Renamer object
        confirmation = renamer.request_confirmation()  # Request the confirmation dictionary from the Renamer
        if self.confirmer(confirmation):  # Ask the user for confirmation, and only continue if the answer is positive
            renamer.confirm(confirmation)  # Confirm the confirmation with the Renamer
            renamer.start_rename()  # Start renaming

        self.show_message_dialog("Renaming Complete!", "")

    def browse_directory(self, widget: object) -> None:
        """
        Shows a directory chooser dialog and sets the entry to the result of the browse

        :param widget: the button that called this method
        :return: None
        """
        if widget is not None:  # Suppress IDE warnings
            selected_directory = self.show_directory_chooser_dialog()  # Open directory chooser dialog
            if selected_directory:  # If a directory was selected set the text entry to that directory path
                self.set_text_entry_string(self.entry, selected_directory)

    def confirmer(self, confirmation: List[Dict[str, str]]) -> bool:
        """
        Asks the user for confirmation before continuing the renaming process

        This is done by the user clicking the 'Yes' Button on every Yes/No Dialog shown,
        each representing one renaming operation to be commited

        :param confirmation: the confirmation dictionary
        :return: False if the user did not confirm the rename, True otherwise.
        """

        for element in confirmation:  # Iterate over every element in the dictionary
            # Generate the message String
            message = "Rename\n"
            message += element["old"]  # Include the old name
            message += "\nto\n"
            message += element["new"]  # Include the new name
            message += "\n?"
            response = self.show_yes_no_dialog("Confirmation", message)  # Show a yes/no dialog
            if not response:
                return False  # as soon as the user disapproves one operation, halt the renaming process
        return True  # If that doesn't happen, return True
