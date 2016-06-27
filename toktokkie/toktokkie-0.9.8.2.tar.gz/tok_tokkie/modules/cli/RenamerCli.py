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

from tok_tokkie.modules.cli.GenericCli import GenericCli
from tok_tokkie.modules.utils.Renamer import Renamer


class RenamerCli(GenericCli):
    """
    CLI for the Renamer plugin, that lets the user choose a directory to use the renamer on.
    The directory's content is evaluated and the proposed changes are then printed to the console,
    where the user can then either approve or cancel the renaming process.
    """

    def __init__(self, parent: GenericCli) -> None:
        """
        Constructor of the RenamerCli, which only calls the GenericCli's constructor
        with the CLI's parent as argument.

        :param parent: the parent cli of the RenamerCli
        :return: None
        """
        super().__init__(parent)

    def start(self, title: str = None) -> None:
        """
        Starts the plugin main loop by indefinitely looping the mainloop() method using the
        start() method of the GenericCli class with the title 'RENAMER PLUGIN'

        :param title: Just a dummy argument to maintain the same method signature as the GenericCli class
        :return: None
        """
        super().start("RENAMER PLUGIN\n")

    def mainloop(self, directory: str = None, noconfirm: bool = None) -> None:
        """
        Starts the renaming process. It can be run in both an interactive and an argument-driven mode
        not requiring user interaction.

        :param directory: Can be set to override the directory and bypassing user input
        :param noconfirm: If this is True, the renaming skips the confirming part
        :return: None
        """
        # If interactive mode is running, ask the user for a directory path
        if directory is None:
            directory = self.ask_user("Enter the show/series directory path:\n")

        # Strip surrounding quotation marks
        if directory.startswith("'") and directory.endswith("'") \
                or directory.startswith("\"") and directory.endswith("\""):
            directory = directory[1:-1]

        # If the directory is not a valid directory, exit immediately
        if not os.path.isdir(directory):
            print("Not a valid directory path")
            return

        # Now that the directory is known, try to rename the contents
        renamer = Renamer(directory)  # Create a new Renamer object

        if not noconfirm:  # We need a manual confirmation by the user
            confirmation = renamer.request_confirmation()  # Request a confirmation
            if self.confirmer(confirmation):  # ask the user for confirmation, if successful start renaming
                print("Renaming...")  # Let the user know we started renaming
                renamer.confirm(confirmation)  # Confirm the renaming process with the Renamer object
                renamer.start_rename()  # Start renaming
                print("Renaming successful.")  # Let the user know we have successfully renamed the files
            else:
                print("Renaming cancelled.")  # Message shown when the user cancels the process
        else:
            renamer.start_rename(True)  # Rename without confirmation, potentially dangerous

    @staticmethod
    def confirmer(confirmation: List[Dict[str, str]]) -> bool:
        """
        Asks the user for confirmation before continuing the renaming process

        This is done by listing all changes to be made and asking the user a simple
        (y/n) question

        :param confirmation: the confirmation
        :return: False if the user did not confirm the rename, True otherwise.
        """
        # iterate over the confirmation list
        for element in confirmation:
            print("OLD: " + element["old"])  # This is the old name of the file
            print("NEW: " + element["new"] + "\n")  # This is the new name of the file

        # Ask for confirmation
        response = input("Proceed with renaming? This can not be undone. (y/n)")

        # If the answer was a lower-case y, return True, False otherwise
        return response == "y"
