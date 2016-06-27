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
import random
import shlex
import struct
import sys
import time

import irc.client
from tok_tokkie.modules.utils.ProgressStruct import ProgressStruct


class IrcLibImplementation(irc.client.SimpleIRCClient):
    """
    This class extends the SimpleIRCClient Class to download XDCC packs using the irclib library
    It is based on the tutorial scripts on the library's Github page, but strongly modified to suit the
    needs of the batch download manager.
    """

    server = ""
    """
    The server address of the server the downloader has to connect to.
    """

    channel = ""
    """
    The channel name of the channel the downloader has to join.
    """

    bot = ""
    """
    The bot serving the requested file
    """

    pack = -1
    """
    The pack number of the file to be downloaded
    """

    destination_directory = ""
    """
    The directory to which the file should be downloaded to
    """

    nickname = ""
    """
    A nickname for the bot
    """

    progress_struct = None
    """
    A progress struct to share the download progress between threads
    """

    filename = ""
    """
    The path to the downloaded file
    """

    file = None
    """
    The downloaded file opened for writing
    """

    dcc = None
    """
    The established DCC connection to the file server bot
    """

    time_counter = int(time.time())
    """
    Keeps track of the time to control how often status updates about the download are printed to the console
    """

    def __init__(self, server: str, channel: str, bot: str, pack: int, destination_directory: str,
                 progress_struct: ProgressStruct, file_name_override: str = None) -> None:
        """
        Constructor for the IrcLibImplementation class. It initializes the base SimpleIRCClient class
        and stores the necessary information for the download process as class variables

        :param server: The server to which the Downloader needs to connect to
        :param channel: The channel the downloader needs to join
        :param bot: The bot serving the file to download
        :param pack: The pack number of the file to download
        :param destination_directory: The destination directory of the downloaded file
        :param progress_struct: The progress struct to keep track of the download progress between threads
        :param file_name_override: Can be set to pre-determine the file name of the downloaded file
        :return: None
        """
        # Initialize base class
        super().__init__()

        # Store values
        self.server = server
        self.channel = channel
        self.bot = bot
        self.pack = pack
        self.destination_directory = destination_directory
        self.progress_struct = progress_struct

        # If a file name is pre-defined, set the file name to be that name.
        if file_name_override is not None:
            self.filename = os.path.join(destination_directory, file_name_override)

    def connect(self) -> None:
        """
        Connects to the server with a randomly generated username
        :return: None
        """
        self.nickname = "media_manager_python" + str(random.randint(0, 1000000))  # Generate random nickname
        print("Connecting to server " + self.server + " at port 6667 as user " + self.nickname)
        super().connect(self.server, 6667, self.nickname)  # Connect to server

    def start(self) -> str:
        """
        Starts the download process and returns the file path of the downloaded file once the download completes
        :return: the path to the downloaded file
        """
        self.connect()  # Connect to server
        try:
            super().start()  # Start the download
        except SystemExit:
            pass  # If disconnect occurs, catch and ignore the system exit call
        except irc.client.ServerConnectionError:
            # If connecting to the server fails, let the user know
            print("Failed to connect to server")
        return self.filename  # Return the file path

    def on_welcome(self, connection: irc.client.ServerConnection, event: irc.client.Event) -> None:
        """
        Method run when the IRCClient successfully connects to a server. It joins the specified channel
        at this stage.

        :param connection: The IRC connection
        :param event: The event that caused this method to be run
        :return: None
        """
        # Make Pycharm happy
        if event is None:
            return

        print("Connected to server")
        print("Joining channel " + self.channel)
        connection.join(self.channel)  # Join the channel

    def on_join(self, connection: irc.client.ServerConnection, event: irc.client.Event) -> None:
        """
        Once the IRCClient successfully joins a channel, the DCC SEND request is sent to the file serving bot

        :param connection: The IRC connection
        :param event: The event that caused this method to be run
        :return: None
        """
        # Make Pycharm happy
        if connection is None or event is None:
            return

        if event.source.startswith(self.nickname):
            print("Joined channel")
            print("Sending DCC SEND request for pack " + str(self.pack) + " to " + self.bot)
            # Send a private message to the bot to request the pack file (xdcc send #packnumber)
            self.connection.privmsg(self.bot, "xdcc send #" + str(self.pack))

    def on_ctcp(self, connection: irc.client.ServerConnection, event: irc.client.Event) -> None:
        """
        This initializes the XDCC file download, once the server is ready to send the file.

        :param connection: The IRC connection
        :param event: The event that caused this method to be run
        :return: None
        """
        # Make Pycharm happy
        if connection is None:
            return

        # Check that the correct type of CTCP message is received
        try:
            payload = event.arguments[1]
        except IndexError:
            return
        # Parse the arguments
        parts = shlex.split(payload)
        command, filename, peer_address, peer_port, size = parts
        if command != "SEND":  # Only react on SENDs
            return

        print("Receiving file:")
        self.progress_struct.single_size = int(size)  # Store the file size in the progress struct

        # Set the file name, but only if it was not set previously
        if not self.filename:
            self.filename = os.path.join(self.destination_directory, os.path.basename(filename))
        else:
            # Add file extension to override-name
            self.filename += "." + filename.rsplit(".", 1)[1]

        # Check if the file already exists. If it does, delete it beforehand
        if os.path.exists(self.filename):
            os.remove(self.filename)

        self.file = open(self.filename, "wb")  # Open the file for writing
        peer_address = irc.client.ip_numstr_to_quad(peer_address)  # Calculate the bot's address
        peer_port = int(peer_port)  # Cast peer port to an integer value
        self.dcc = self.dcc_connect(peer_address, peer_port, "raw")  # Establish the DCC connection to the bot

    def on_dccmsg(self, connection: irc.client.ServerConnection, event: irc.client.Event) -> None:
        """
        Run each time a new chunk of data is received while downloading

        :param connection: The IRC connection
        :param event: The event that caused this method to be run
        :return: None
        """
        # Make Pycharm happy
        if connection is None:
            return

        data = event.arguments[0]  # Get the received data
        self.file.write(data)  # and write it to file
        self.progress_struct.single_progress += len(data)  # Increase the progress struct's value

        # Print message to the console once every second
        # print()
        if self.time_counter < int(time.time()):  # Check the time
            self.time_counter = int(time.time())  # Update the time counter

            # Format the string to print
            single_progress = float(self.progress_struct.single_progress) / float(self.progress_struct.single_size)
            single_progress *= 100.00
            single_progress_formatted_string = " (%.2f" % single_progress + " %)"
            progress_fraction = str(self.progress_struct.single_progress) + "/" + str(self.progress_struct.single_size)

            # Print, and line return
            print(progress_fraction + single_progress_formatted_string, end="\r")

        # Communicate with the server
        self.dcc.send_bytes(struct.pack("!I", self.progress_struct.single_progress))

    def on_dcc_disconnect(self, connection: irc.client.ServerConnection, event: irc.client.Event) -> None:
        """
        Whenever the download completes, print a summary to the console and disconnect from the IRC network

        :param connection: The IRC connection
        :param event: The event that caused this method to be run
        :return: None
        """
        # Make Pycharm happy
        if connection is None or event is None:
            pass

        self.file.close()  # Close the file
        # Print a summary of the file
        print("Received file %s (%d bytes)." % (self.filename,
                                                self.progress_struct.single_progress))
        self.connection.quit()  # Close the IRC connection

        if self.connection.connected:
            self.on_disconnect(connection, event)

    # noinspection PyMethodMayBeStatic
    def on_disconnect(self, connection: irc.client.ServerConnection, event: irc.client.Event) -> None:
        """
        Stop the program when a disconnect occurs (Gets excepted by the start() method)

        :param connection: The IRC connection
        :param event: The event that caused this method to be run
        :return: None
        """
        # Make Pycharm happy
        if connection is None or event is None:
            pass
        sys.exit(0)
