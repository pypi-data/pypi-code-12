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
import sys
from tok_tokkie.modules.cli.exceptions.ReturnException import ReturnException

# Try to import readline, this makes using the CLI much nicer, it is not supported on Windows however
try:
    import readline
except ImportError:
    readline = None


class GenericCli(object):
    """
    Class that defines how a CLI has to react.
    It defines interface structures to somewhat standardize the methods how
    user input is parsed.
    """

    parent = None
    """
    A reference to a possible parent CLI, to which this CLI can return to in case
    quit() is called
    """

    # parent is actually a GenericCli object
    def __init__(self, parent=None) -> None:
        """
        Constructor of the GenericCli Class

        Creates a new CLI object. It has the option to store a reference
        to a parent CLI as a local variable.

        If a parent is specified, the program will return into said parent
        when the stop() method is called. Otherwise, the program will end.

        :param parent: The parent CLI to which the CLI can return to.
                        It is a GenericCli object.
        :return: None
        """
        self.parent = parent

    def start(self, title: str = None) -> None:
        """
        Starts the CLI.

        It loops the mainloop method indefinitely and checks for ReturnExceptions,
        which cause the CLI to return to its parent or quit completely.

        :param title: A string that is shown only once at the beginning of the loop
        :return: None
        """
        # Try/Except to catch ReturnExceptions, which indicate that the user wants to quit
        # the CLI.
        try:
            # Only show the title once, or not at all if none was specified
            if title is not None:
                print(title)

            # This loops the CLI indefinitely
            while True:
                self.mainloop()

        except ReturnException:
            # The print call generates a new empty line as a seperator.
            # This is purely aesthetical.
            print()
            # Stops the CLI
            self.stop()

    def stop(self) -> None:
        """
        Ends the CLI and restarts the parent CLI, or exits with code 0 if no parent was defined.
        :return: None
        """
        if self.parent is not None:
            # Re-starts the parent if it was specified in the constructor
            self.parent.start()
        else:
            # Else the program exits with exit code 0
            sys.exit(0)

    def mainloop(self) -> None:
        """
        This method defines a single loop of the program. It is called repeatedly until the
        CLI quits. This method must be implemented by subclasses of GenericCli
        :return: void
        """
        raise NotImplementedError()

    @staticmethod
    def ask_user(message: str = None, default=None) -> str:
        """
        Creates a user prompt with default behaviours, reducing code reuse.
        It is used like a smarter input() method.

        It checks if the user enters quit, return or exit, in which case the
        method raises a ReturnException which should be handled by the start()
        method.

        This method also supports the use of a default response, which will be returned
        if the user enters an empty string.

        A message can also be displayed to the user before the actual prompt.

        :param message: Optional message to be displayed to the user
        :param default: Optional default value if only enter/return is pressed
        :raises ReturnException: If the user enters quit, return or exit, this
                    Exception is raised in order for the start method to correctly
                    handle this case
        :return: The user input
        """

        # Creates the message string
        prompt_message = ""
        if message is not None:
            prompt_message = message
        if default is not None:
            prompt_message += "[" + default + "]"

        # Asks the user for input
        print(prompt_message, end="")
        user_response = input()

        # Does rudimentary checks of the user input
        if user_response.lower() in ["quit", "return", "exit"]:
            # Raises Exception to quit the CLI
            raise ReturnException
        elif user_response == "" and default is not None:
            # Returns the default string, user entered nothing
            return default
        else:
            # Returns the string entered by the user
            return user_response
