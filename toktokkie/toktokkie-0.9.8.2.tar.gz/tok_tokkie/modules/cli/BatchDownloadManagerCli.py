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
import sys

from tok_tokkie.modules.cli.GenericCli import GenericCli
from tok_tokkie.modules.utils.BatchDownloadManager import BatchDownloadManager
from tok_tokkie.modules.utils.ProgressStruct import ProgressStruct
from tok_tokkie.modules.utils.downloaders.DownloaderManager import DownloaderManager
from tok_tokkie.modules.utils.searchengines.SearchEngineManager import SearchEngineManager


class BatchDownloadManagerCli(GenericCli):
    """
    CLI for the BatchDownloadManager plugin

    It enables the user to search and download XDCC packs
    """

    directory = ""
    """
    The directory path to the show to which the downloaded XDCC Packs belong to
    """

    show_name = ""
    """
    The show name of the files to be downloaded
    """

    season = ""
    """
    The season number of the files to be downloaded
    """

    starting_episode_number = ""
    """
    The first episode number to be downloaded, others will be matched with increments of this number
    """

    search_engine = ""
    """
    Which search engine was selected by the user
    """

    main_icon = ""
    """
    The main icon used for the folder containing the show
    """

    secondary_icon = ""
    """
    The icon for the specific season for which episodes will be downloaded
    """

    iconizer = ""
    """
    Which iconizer method was selected by the user
    """

    selected_packs = []
    """
    A list of the packs selected by the user to download
    """

    auto_rename = False
    """
    Flag that sets if the files should be auto-renamed after the download completes
    """

    def __init__(self, parent: GenericCli = None) -> None:
        """
        Constructor of the BatchDownloadManagerCLi Class
        It calls the Constructor of the GenericCli Class

        :param parent: the parent gui
        :return: None
        """
        super().__init__(parent)

    def start(self, title: str = None) -> None:
        """
        Starts the main program loop with the title 'BATCH DOWNLOAD MANAGER PLUGIN'

        :param title: Just a dummy argument to maintain the same method signature as the GenericCli class
        :return: None
        """
        super().start("BATCH DOWNLOAD MANAGER PLUGIN\n")

    def mainloop(self,
                 directory: str = None, use_defaults: bool = None, show_name_override: str = None,
                 season_number_override: str = None, first_episode_override: str = None,
                 search_engine: str = None, search_term: str = None, auto_rename: bool = None,
                 download_selection_override: str = None) -> None:
        """
        The main program loop

        If called without arguments, the CLI starts in interactive mode, otherwise the given arguments are
        used to define the attributes normally given by the user via the ask_user() method

        All parameters are optional and only used in non-interactive argument mode

        :param directory: The directory path to which the downloaded files are saved
        :param use_defaults: Flag that automatically sets things like show name, season number etc. to values calculated
                                via parsing the target directory's content
        :param show_name_override: This overrides the show name, higher priority than use_defaults
        :param season_number_override: This overrides the season number, higher priority than use_defaults
        :param first_episode_override: This overrides the first episode number, higher priority than use_defaults
        :param search_engine: This is the search engine to be used when searching for XDCC packs
        :param search_term: The search term to be used in the xdcc search, higher priority than use_defaults
        :param auto_rename: Flag that sets if the progra should automatically rename files according to thetvdb.com
        :param download_selection_override: A selection of packs to download can be specified here as a
                                            comma-delimited string of index numbers
        :return: None
        """
        self.restore_start_state()  # This resets the class variables to their default state

        # Sanity check:
        # This checks if only valid option types were selected
        valid = \
            (directory is None and use_defaults is None and show_name_override is None and
             season_number_override is None and first_episode_override is None and search_engine is None and
             search_term is None and auto_rename is None and download_selection_override is None) ^ \
            (directory is not None and use_defaults and search_engine is not None and auto_rename is not None and
             download_selection_override is not None) ^ \
            (directory is not None and not use_defaults and show_name_override is not None and
             season_number_override is not None and first_episode_override is not None and
             search_engine is not None and search_term is not None and auto_rename is not None and
             download_selection_override is not None)

        # If an invalid option was found, notify the user and end the program
        if not valid:
            # The string has to be stored in a variable to mitigate syntax errors in python2
            string_out = "Invalid combination of arguments. This should not be happening, please contact the "
            string_out += "developer at hermann@krumreyh.com to make him fix the issue."
            print(string_out)
            sys.exit(1)

        # Finds out target directory
        self.directory = directory  # Set it to given parameter (May be None)
        if self.directory is None:  # Interactive Mode
            self.directory = self.ask_user("Enter the target download directory:")
        if not self.directory:  # Check if directory was entered
            print("Invalid directory")
            return

        # Strip surrounding quotation marks
        if self.directory.startswith("'") and self.directory.endswith("'")\
                or self.directory.startswith("\"") and self.directory.endswith("\""):
            self.directory = self.directory[1:-1]

        # calculate show name, season number and first episode number from the given directory
        # Also calculates the main and secondary icon locations
        # These are subject to be changed by the user
        show_name, season, starting_episode_number, main_icon, secondary_icon = \
            BatchDownloadManager.analyse_show_directory(self.directory)

        # This is used in interactive mode
        if directory is None:

            # Asks the user for the show name, defaults to the calculated one from before
            self.show_name = self.ask_user("Please enter the show name:", default=show_name)
            if os.path.basename(self.directory) != self.show_name:
                response = self.ask_user("Are you sure that " + self.show_name + " is correct? (y/n)")
                if response.lower() != "y":
                    return  # End this loop if user says no.

            # Gets the season number from the user
            # loops until the user gives a valid response
            while self.season == "":
                try:
                    self.season = int(self.ask_user("Please enter the season number:", default=season))
                except ValueError:
                    "Invalid integer value.\n"

            # Gets the first episode number from the user
            # loops until the user gives a valid response
            while self.starting_episode_number == "":
                try:
                    self.starting_episode_number = int(self.ask_user("Please enter the first episode number:",
                                                                     default=starting_episode_number))
                except ValueError:
                    "Invalid integer value.\n"

            # Starts the XDCC search part
            self.search_xdcc()

        # This is used in non-interactive argument mode
        else:
            if use_defaults is not None:  # If the 'use defaults' flag is set, just take the calculated values.
                self.show_name = show_name
                self.season = season
                self.starting_episode_number = starting_episode_number
            # But they can still be override, the single overrides have higher priority
            if show_name_override is not None:
                self.show_name = show_name_override
            if season_number_override is not None:
                self.season = season_number_override
            if first_episode_override is not None:
                self.starting_episode_number = first_episode_override
            if search_term is None:
                search_term = self.show_name

            # Start the XDCC search part with override parameters
            self.search_xdcc(search_engine, search_term, download_selection_override)

        # If in interactive mode, ask the user if he would like the files to be auto-renamed
        if auto_rename is None:

            auto_rename_prompt = self.ask_user("Auto Rename? (y/n)")
            if auto_rename_prompt == "y":
                self.auto_rename = True
            else:
                self.auto_rename = False

        # Else we just take the option given via parameter
        else:
            self.auto_rename = auto_rename

        self.start_download()  # Start the download!

    def search_xdcc(self, search_engine_override: str = None, search_term_override: str = None,
                    download_selection_override: str = None) -> None:
        """
        Searches packlists for xdcc packs.

        In interactive mode, this asks the user to specify a search engine and search term, then the results are
        displayed and the user can select which packs he wants to download by specifying a comma-seperated
        string of index numbers. The index numbers are displayed when listing the search results.

        In argument parse mode, the user interaction can be completely bypassed.

        :param search_engine_override: Used to override the search engine in argument mode
        :param search_term_override: Used to override the search term in argument mode
        :param download_selection_override: Can be specified to automatically select packs from the search results
        :return: None
        """

        searching = True  # True as long as the search isn't done
        print("Starting Search Procedure:")  # Let the user know that we've started the search procedure
        while searching:
            # This can override the search engine via the arguments
            if search_engine_override is not None:
                search_engine_selected = True
                self.search_engine = search_engine_override
            else:
                search_engine_selected = False
            # But if not specified, ask the user until he gives a satisfactory answer
            while not search_engine_selected:

                # These are the search engines that are available
                search_engine_options = SearchEngineManager.get_search_engine_strings()

                print("Search Engine Options:\n")

                # List all search engine options:
                i = 1  # Index starts y one
                for search_engine in search_engine_options:
                    print(str(i) + ": " + search_engine)
                    i += 1  # increase index

                try:
                    # ask the user for the search engine index
                    search_engine = int(self.ask_user("Which search engine would you like to use?", default="1"))

                    i = 1  # Start index at 1 again
                    valid_selection = False  # Flag that gets set when a valid search engine index was selected
                    for search_engine_option in search_engine_options:  # Checks all search_engine options
                        if search_engine == i:  # If the index fits
                            valid_selection = True  # Set the flag
                            self.search_engine = search_engine_option  # and set the search engine
                            break  # We know that the loop is no longer needed, so we break out of it
                        i += 1  # Increment the index to check

                    # If the given index is out of bounds, let the user know, ask him again
                    if not valid_selection:
                        print("Invalid index")
                        continue
                    # Otherwise leave the search engine loop
                    else:
                        search_engine_selected = True

                except ValueError:
                    # If user didn't enter a int value
                    print("Not a valid integer")

            # Establish the search term, ask user if not specified
            search_term = search_term_override
            if search_term_override is None:
                search_term = self.ask_user("Search for what?", default=self.show_name)

            print("searching...")  # Let user know we're searching
            search_result = BatchDownloadManager.conduct_xdcc_search(self.search_engine, search_term)
            print("Results:")  # Let user know the search has completed

            # Print the results to the console
            i = 0
            # and store them in this dictionary, with the index numbers being the keys
            # for the individual XDCCPack objects
            result_dict = {}
            for result in search_result:
                result_dict[i] = result  # Store to dictionary
                print(str(i) + " " + result.to_string())  # Print together with the index number
                i += 1

            if download_selection_override is not None and download_selection_override == "":
                # Stop the program, if no packs were specified in args mode.
                # This means that the program was used in search mode, and the search has already concluded
                sys.exit(0)

            # Now the selection begins:
            selecting = True
            while selecting:  # Continue the selection until the user has reached a decision

                if download_selection_override is None:
                    # Ask the user for their selection (Only if no override was used)
                    selection = self.ask_user("Enter a comma-delimited selection of packs to download, "
                                              "or blank to conduct a new search:\n")

                    if selection == "":
                        # If nothing was selected, conduct a new search
                        break
                else:
                    selection = download_selection_override

                selection_list = selection.split(",")  # Split indexes from each other
                selected_packs = []  # Create a list to store the selected packs

                # Check the validity of the user input
                try:
                    for selected in selection_list:
                        selected_packs.append(result_dict[int(selected)])
                except ValueError:
                    # If a non-integer value was entered
                    print("Invalid selection type, please only enter the index of the packs you want to select")
                    continue
                except KeyError:
                    # If a index was specified that was out of bounds
                    print("Invalid index selected")
                    continue

                print("Selection:")
                # Print the selection of packs to the console
                for pack in selected_packs:
                    print(pack.to_string())

                if download_selection_override is None:
                    # ask the user once more if he/she wants to download the packs
                    confirmation = self.ask_user("Do you want to download these packs? (y/n)")
                    if confirmation == "y":  # Confirmed by user,
                        searching = False  # stopping the search and
                        selecting = False  # select loop
                        self.selected_packs = selected_packs  # and store the selection as class variable
                    else:  # Not confirmed by user.
                        # Now the user can either make a new search, or a new selection
                        re_search_prompt = self.ask_user("Do you want to re-search? (y/n)")
                        if re_search_prompt == "y":  # Conduct new search
                            selecting = False  # We are now no longer selecting
                else:
                    self.selected_packs = selected_packs

    def start_download(self) -> None:
        """
        This method starts the download procedure using the previously determined variables

        It uses the common methods from the BatchDownloadManager class to accomplish this and
        also perfor basic checks if all entered data is valid

        :return: None
        """

        # Prepare the download:
        # Makes calculations as well as sanity/validity checks
        preparation = BatchDownloadManager.prepare(self.directory,
                                                   self.show_name,
                                                   str(self.season),
                                                   str(self.starting_episode_number),
                                                   self.main_icon,
                                                   self.secondary_icon,
                                                   self.iconizer)

        # If errors occur during the preparation, a 2-part tuple is returned with a description of the error
        # Afterwards, the method returns without doing anything
        if len(preparation) != 6:
            print(preparation["error_title"])
            print(preparation["error_text"])
            return

        # If the preparation was successful, the download process will now start
        print("Downloading...")  # Let the user know that we started downloading

        # For command line, use a CLI downloader per default
        downloader = DownloaderManager.get_downloader_strings("cli")[0]
        progress = ProgressStruct()  # Create a progress structure to keep track of download progress
        progress.total = len(self.selected_packs)  # Define how many files are going to be downloaded

        # Start downloading
        BatchDownloadManager.start_download_process(
            preparation, downloader, self.selected_packs, self.auto_rename, progress)

        print("Download complete")  # Let the user know that the downloads have all completed

    def restore_start_state(self) -> None:
        """
        Restores the state of the BatchDownloadManagerCli class variables to what they were at the beginning.

        :return: None
        """

        # Reset everything
        self.directory = ""
        self.show_name = ""
        self.season = ""
        self.starting_episode_number = ""
        self.search_engine = ""
        self.main_icon = ""
        self.secondary_icon = ""
        self.iconizer = ""
        self.selected_packs = []
        self.auto_rename = False
