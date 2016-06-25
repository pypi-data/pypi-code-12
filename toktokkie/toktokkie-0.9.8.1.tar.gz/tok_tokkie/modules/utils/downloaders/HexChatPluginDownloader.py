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
import platform
import time
from subprocess import Popen
from threading import Thread
from typing import List

from tok_tokkie.modules.utils.fileops.FileMover import FileMover
from tok_tokkie.modules.objects.Episode import Episode
from tok_tokkie.modules.objects.XDCCPack import XDCCPack
from tok_tokkie.modules.utils.ProgressStruct import ProgressStruct
from tok_tokkie.modules.utils.downloaders.GenericDownloader import GenericDownloader


class HexChatPluginDownloader(GenericDownloader):
    """
    XDCC Downloader that makes use of Hexchat's python scripting interface

    This Downloader requires that Hexchat is properly installed on the user's
    system, along with the python plugin for hexchat.
    """

    script_location = ""
    """
    The location of the script that hooks into Hexchat to start the downloading process
    It is contained in the addons directory of the hexchat configuration directory
    """

    hexchat_config_location = ""
    """
    The path to the hexchat configuration file
    """

    packs = []
    """
    A list of packs to be downloaded
    """

    progress_struct = None
    """
    A ProgressStruct object which can be used by for example a graphical user interface for
    cross-thread communication, so that the GUI knows the current progress of the download
    """

    target_directory = ""
    """
    The target directory for the downloaded files
    """

    download_dir = ""
    """
    The download directory to which the files will initially be downloaded to
    """

    script = None
    """
    The script object, opened by the __init__ method with the location of the script file
    It is opened in write mode, which erases previous content and generates this file
    if it did not exist beforehand
    """

    show_name = ""
    """
    The name of the show of which files are downloaded for
    (Only used when auto-renaming)
    """

    episode_number = -1
    """
    The episode number of the first episode to be downloaded
    (Only used when auto-renaming)
    """

    season_number = -1
    """
    The season number for the files currently being downloaded
    (Only used when auto-renaming)
    """

    downloading = False
    """
    Keeps track if the program is currently downloading or not
    """

    auto_rename = False
    """
    This boolean is True if the program is supposed to automatically rename the downloaded files,
    but otherwise it defaults to False
    """

    # noinspection PyTypeChecker
    def __init__(self, packs: List[XDCCPack], progress_struct: ProgressStruct, target_directory: str,
                 show_name: str = "", episode_number: int = 0, season_number: int = 0) -> None:
        """
        Constructor for the HexChatPluginDownloader

        It takes information on the files to download as parameters, stores them locally using the
        GenericDownloader's Constructor and then calculates various file system paths etc. as well
        as ensure that the Hexchat configuration is correct

        :param packs: a list of the packs to be downloaded
        :param progress_struct: Structure to keep track of download progress
        :param target_directory: The target download directory
        :param show_name: the show name for use with auto_rename
        :param episode_number: the (first) episode number for use with auto_rename
        :param season_number: the season number for use with auto_rename
        :return: None
        """
        super().__init__(packs, progress_struct, target_directory, show_name, episode_number, season_number)

        # Platform check: Different paths for different systems
        if platform.system() == "Linux":
            self.script_location = os.path.join(os.path.expanduser('~'), ".config", "hexchat", "addons", "dlscript.py")
            self.hexchat_config_location = os.path.join(os.path.expanduser('~'), ".config", "hexchat", "hexchat.conf")
        elif platform.system() == "Windows":
            self.script_location = os.path.join(os.path.expanduser('~'),
                                                "AppData", "Roaming", "HexChat", "addons", "dlscript.py")
            self.hexchat_config_location = os.path.join(os.path.expanduser('~'),
                                                        "AppData", "Roaming", "HexChat", "hexchat.conf")

        # Store parameters
        self.download_dir = target_directory

        current_dl_dir = ""  # Temporary variable to hold the download directory specified by the config file

        # Read the hexchat config file
        hexchat_config = open(self.hexchat_config_location, 'r')  # open file for reading
        content = hexchat_config.read().split("\n")  # read text from file line-wise
        hexchat_config.close()  # Close file
        new_content = []  # Initialize empty list to store the new content of the file once everything was verified

        for line in content:  # Parse the lines
            if "gui_join_dialog" in line:
                new_content.append("gui_join_dialog = 0")  # Disables the join dialog
            elif "dcc_auto_recv" in line:
                new_content.append("dcc_auto_recv = 2")  # Enables DCC Auto Receive, no user interaction necessary
            elif "gui_slist_skip" in line:
                new_content.append("gui_slist_skip = 1")  # Skips the server list
            elif "dcc_dir = " in line:
                current_dl_dir = line.split("dcc_dir = ")[1].split("\n")[0]  # Temporarily saves current download dir
                new_content.append("dcc_dir = " + self.download_dir)  # Sets download directory to target_directory
            else:
                new_content.append(line)
        new_content.pop()

        # TODO get this to work on Windows
        # There are some weird reading issues if this runs on Windows at the moment,
        # the current solution is to fall back to using the current configuration of hexchat
        if platform.system() == "Linux":
            # This writes the new config file to the hexchat config
            hexchat_config = open(self.hexchat_config_location, 'w')  # open the config file
            for line in new_content:  # Write every line to the file
                hexchat_config.write(line + "\n")  # rite the line + newline character
            hexchat_config.close()  # Close the config file
        elif platform.system() == "Windows":
            self.download_dir = current_dl_dir  # Reset the download directory to the one stored in the original config

    def __write_start__(self) -> None:
        """
        Writes the beginning of the downloader script to the opened script file

        It defines the metadata used by Hexchat's scripting engine, handles imports,
        defines methods for downloading and listener methods for when downloads
        fail or complete successfully

        :return: None
        """
        script_start = [  # This is metadata required by the Hexchat scripting engine
            "__module_name__ = \"xdcc_executer\"",
            "__module_version__ = \"1.0\"",
            "__module_description__ = \"Python XDCC Executer\"\n",

            # imports
            "import hexchat",
            "import sys\n",

            # starts a download
            "def download(word, word_eol, userdata):",
            "\thexchat.command(packs[0])",  # send download message
            "\treturn hexchat.EAT_HEXCHAT\n",  # Eat stdout

            # method run when a download completes successfully
            "def downloadComplete(word, word_eol, userdata):",
            "\thexchat.command('quit')",  # Quits the current channel
            "\tchannels.pop(0)",  # Removes the channel from which the pack was downloaded
            "\tpacks.pop(0)",  # Removes the downloaded pack
            "\tif len(channels) == 0:",  # If all downloads complete
            "\t\tsys.exit(0)",  # Exit the program
            "\telse:",  # Else download the next file
            "\t\thexchat.command(channels[0])",  # Join next channel
            "\treturn hexchat.EAT_HEXCHAT\n",  # Eat stdout

            # method run when a download fails
            "def downloadFailed(word, word_eol, userdata):",
            "\tfailed.append(packs[0])",  # append to failed packs
            "\thexchat.command('quit')",  # Quit the current channel
            "\tchannels.pop(0)",  # Remove the last used channel
            "\tpacks.pop(0)",  # Remove the last used pack
            "\tif len(channels) == 0:",  # If done,
            "\t\tsys.exit(1)",  # quit the program
            "\telse:",  # continue otherwise
            "\t\thexchat.command(channels[0])",  # join next channel
            "\treturn hexchat.EAT_HEXCHAT\n",  # eat stdout

            # Variables
            "failed = []",  # List of failed packs
            "channels = []",  # List of channels
            "packs = []\n"]  # List of packs to download

        for line in script_start:  # Write to file
            self.script.write(line + "\n")

    def __write_end__(self) -> None:
        """
        Writes the end of the downloader script

        It implements the hooks into hexchat's hook system with which
        the script can react to different status changes and events

        :return: None
        """
        script_end = ["hexchat.command(channels[0])",  # This joins the first channel, starting the downloads
                      "hexchat.hook_print(\"You Join\", download)",  # Runs download() once connected to a channel
                      # Runs downloadComplete if a download completes
                      "hexchat.hook_print(\"DCC RECV Complete\", downloadComplete)",
                      # Runs downloadFailed() if a download stalls
                      "hexchat.hook_print(\"DCC STALL\", downloadFailed)",
                      # Runs downloadFailed() if a download is aborted
                      "hexchat.hook_print(\"DCC RECV Abort\", downloadFailed)",
                      # Runs downloadFailed() if a download fails
                      "hexchat.hook_print(\"DCC RECV Failed\", downloadFailed)",
                      # Runs downloadFailed() if a download times out
                      "hexchat.hook_print(\"DCC Timeout\", downloadFailed)"]

        for line in script_end:  # Write to file
            self.script.write(line + "\n")

    def __write_script__(self, pack: XDCCPack) -> None:
        """
        Writes the downloader script to the script file an closes the file

        :return: None
        """
        self.script = open(self.script_location, 'w')  # Opens the script file for writing
        self.__write_start__()  # Write the start of the file
        # Write middle section of the file, specifying the pack and channel to be downloaded from
        self.script.write("channels.append(\"newserver irc://" + pack.server + "/" + pack.channel + "\")\n")
        self.script.write("packs.append(\"msg " + pack.bot + " xdcc send #" + str(pack.packnumber) + "\")\n")
        self.__write_end__()  # Write the end of the script
        self.script.close()  # Close the script file

    def download_single(self, pack: XDCCPack) -> str:
        """
        Downloads a single pack using the Hexchat Downloader Script

        This does not work if no working Hexchat installation (including the Hexchat python scripting plugin)
        is present on the user's system.

        The downloaded files are also renamed and moved if this is specified.

        :param pack: The pack to be downloaded
        :return: The path to the downloaded file
        """
        # Create new thread that updates the Progress Struct
        progress_thread = Thread(target=self.update_progress, args=(pack,))

        self.__write_script__(pack)  # Write download script for the pack to download
        self.downloading = True  # Sets the downloading boolean to let other threads know that the download is running
        progress_thread.start()  # Start the progress updater thread

        # Starts Hexchat
        if platform.system() == "Linux":
            Popen(["hexchat"]).wait()
        elif platform.system() == "Windows":
            if os.path.isfile("C:\\Program Files\\HexChat\\hexchat.exe"):
                Popen(["C:\\Program Files\\HexChat\\hexchat.exe"]).wait()
        # Download Complete

        self.downloading = False  # Let other thread know we're done
        os.remove(self.script_location)  # Deletes script file

        # Process file further:

        file_path = os.path.join(self.download_dir, pack.filename)
        if self.auto_rename:  # Automatically renames the file if specified
            # Creates Episode object
            episode = Episode(file_path, self.episode_number, self.season_number, self.show_name)
            episode.rename()  # Auto-tvdb-renames the file
            file_path = episode.episode_file  # Changes file path variable to reflect the new path to the renamed file
            self.episode_number += 1  # Increment episode number for next episode
        # else the file path just stays the same

        if self.download_dir != self.target_directory:  # If target dir is not download dir, move files to target dir
            file_path = FileMover.move_file(file_path, self.target_directory)  # Move file to target directory

        return file_path

    def update_progress(self, pack: XDCCPack) -> None:
        """
        Updates the progress structure based on how far the download has progressed
        :param pack: The pack that is currently being downloaded
        :return: None
        """
        # Find out approximate size of the file to download
        self.progress_struct.single_size = pack.size

        while self.downloading:  # Update progress while the file is downloading
            try:
                # Get the current file size of the program
                self.progress_struct.single_progress = os.path.getsize(os.path.join(self.download_dir, pack.filename))
            except os.error:
                # If the file does not exist yet, set the progress to 0
                self.progress_struct.single_progress = 0
            time.sleep(1)  # Always sleep a second between updates

    @staticmethod
    def get_string_identifier() -> str:
        """
        Returns a unique string identifier with which the Downloader can be addressed by
        the DownloaderManager

        :return: the string identifier of the Downloader
        """
        return "Hexchat Downloader"
