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
import time
from tok_tokkie.modules.utils.searchengines.SearchEngineManager import SearchEngineManager
from tok_tokkie.modules.utils.BatchDownloadManager import BatchDownloadManager
from tok_tokkie.modules.utils.downloaders.DownloaderManager import DownloaderManager
from tok_tokkie.modules.utils.ProgressStruct import ProgressStruct
from tok_tokkie.modules.utils.DeepIconizer import DeepIconizer
from tok_tokkie.metadata import Globals


class BatchDownloadManagerGui(Globals.selected_grid_gui_framework):
    """
    GUI for the BatchDownloadManager plugin
    """

    # Threading Variables
    search_thread = None
    """
    A thread that runs in parallel to the GUI's main thread. It conducts XDCC searches without freezing the GUI
    """

    searching = False
    """
    Indicator if an XDCC search is currently in progress
    """

    dl_progress = None
    """
    The download progress structure used to communicate with the actual downloader
    """

    # GUI Elements
    configure_label = None
    """
    A text Label that displays "Options" above the various configuration options
    """

    destination_label = None
    """
    A Text Label used as an indicator that the Text Entry beside it is used to determine the
    destination directory of the download
    """

    destination = None
    """
    The Text Entry that determines the destination directory for the download
    """

    destination_browser = None
    """
    A Button that enables browsing for a target download directory
    """

    show_label = None
    """
    A Text Label that indicates that the Text Entry beside it is used as a means of storing the
    Show Name of the files to download
    """

    show = None
    """
    The Text Entry that stores the show name of the packs to be downloaded
    This Entry is updated whenever the 'destination' Entry is changed
    """

    season_label = None
    """
    A text label that indicates that the Entry beside it is used to store the season number of the show to be
    downloaded.
    """

    season = None
    """
    The Text Entry storing the season number of the show to be downloaded, it is automatically updated whenever the
    'destination' Entry is changed
    """

    episode_label = None
    """
    A text label that indicates that the Entry beside it is used to store the first episode number of the show to be
    downloaded.
    """

    episode = None
    """
    The Text Entry storing the first episode number of the show to be downloaded, it is automatically updated whenever
    the 'destination' Entry is changed
    """

    search_label = None
    """
    A text Label that indicates that the Entry beside it is used to store the search term used when conducting the
    XDCC search
    """

    search_field = None
    """
    Text Entry that stores the search term used when conducting the XDCC search. It is automatically updated to be the
    same as the 'show' Entry whenever the 'destination' Entry is modified
    """

    search_engine_label = None
    """
    Text Label that indicates that the Combo Box beside it is used to select which search engine to use
    """

    search_engine_combo_box = None
    """
    Combo Box using string values to identify which search engine should be used to conduct the XDCC search
    """

    search_button = None
    """
    Button that starts the XDCC search process with the currently entered information
    """

    download_engine_label = None
    """
    Text Label that indicates that the Combo Box beside it is used to select which downloader to use
    """

    download_engine_combo_box = None
    """
    Combo Box using string values to identify which downloader should be used when downloading XDCC packs
    """

    download_button = None
    """
    The button that starts the download process of the currently selected XDCC packs
    """

    rename_check = None
    """
    A Checkbutton used to select if the downloaded files should be automatically renamed once they have
    completed downloading.
    """

    main_icon_label = None
    """
    A Text Label indicating that the Text Entry beside it is used to store the main icon label's path
    """

    main_icon_location = None
    """
    A Text Entry used to store the main icon label's path
    """

    secondary_icon_label = None
    """
    A Text Label indicating that the Text Entry beside it is used to store the secondary icon label's path
    """

    secondary_icon_location = None
    """
    A Text Entry used to store the secondary icon label's path
    """

    method_label = None
    """
    A Text Label indicating that the Combo Box beside it is used to select the iconizing method to be used
    with the selected icons
    """

    method_combo_box = None
    """
    A Combobox with string options used to select the iconizing method to be used with the selected icons
    """

    search_results = None
    """
    A List Box with multiple columns allowing multiple selections that displays the results of an XDCC search
    """

    search_results_label = None
    """
    A Text Label displayed above the search results displaying "Search Results"
    """

    directory_content = None
    """
    A List Box with multiple columns allowing multiple selections that displays the content of the currently selected
    directory's highest season's content
    """

    directory_content_label = None
    """
    A Text Label displayed above the directory content displaying "Episodes"
    """

    total_progress_bar = None
    """
    A Progress bar displaying the total progress of the downloading process
    """

    total_progress_label = None
    """
    A Label indicating that the total progress is displayed beside it
    """

    total_progress_current = None
    """
    A Text Label that shows the current total progress in amount of files
    """

    total_progress_total = None
    """
    A Text Label that shows the total amount of files to be downloaded
    """

    single_progress_bar = None
    """
    A Progress bar displaying the download progress of the current file
    """

    single_progress_label = None
    """
    A Text Label that indicates that the single progress is displayed beside it
    """

    single_progress_current = None
    """
    A Text label that shows how many bytes of the current were already downloaded by the downloader
    """

    single_progress_total = None
    """
    A Text label that shows how many bytes the size of the current file is
    """

    download_speed = None
    """
    A Text Label displaying the current download speed
    """

    download_speed_label = None
    """
    A Text Label indicating that the current download speed is displayed beside it
    """

    average_dl_speed = None
    """
    A Text Label showing the average download speed over the course of the entire download
    """

    average_dl_speed_label = None
    """
    A Text Label indicating that beside it is a Text Label showing the average download speed over
    the course of the entire download
    """

    time_left = None
    """
    A Text Label showing an approximation on how much time will pass until the download is completed
    """

    time_left_label = None
    """
    A Text Label indicating that beside it is a Text Label showing an approximation on how much time will pass
    until the download is completed
    """

    # Other
    search_result = []
    """
    A list of search results from an XDCC search
    """

    def __init__(self, parent: Globals.selected_grid_gui_framework) -> None:
        """
        Constructor for the BatchDownloadManagerGui class

        It initializes a gfworks Window with the title "Batch Download Manager" and
        hides the parent window.

        :param parent: the parent gui
        :return: None
        """
        super().__init__("Batch Download Manager", parent, True)

    def lay_out(self):
        """
        Sets up all interface elements of the GUI and positions them in a Grid Layout

        :return: None
        """
        self.configure_label = self.generate_label("Options")
        self.position_absolute(self.configure_label, 0, 0, 40, 5)

        self.destination_label = self.generate_label("Destination Directory")
        self.destination = self.generate_text_entry("", on_changed_command=self.on_directory_changed)
        self.destination_browser = self.generate_button("Browse", self.browse_for_destination)
        self.position_absolute(self.destination_label, 0, 5, 8, 5)
        self.position_absolute(self.destination_browser, 10, 5, 8, 5)
        self.position_absolute(self.destination, 20, 5, 20, 5)

        self.show_label = self.generate_label("Show Name")
        self.show = self.generate_text_entry("")
        self.position_absolute(self.show_label, 0, 10, 20, 5)
        self.position_absolute(self.show, 20, 10, 20, 5)

        self.season_label = self.generate_label("Season Number")
        self.season = self.generate_text_entry("")
        self.position_absolute(self.season_label, 0, 15, 20, 5)
        self.position_absolute(self.season, 20, 15, 20, 5)

        self.episode_label = self.generate_label("Starting Episode Number")
        self.episode = self.generate_text_entry("optional")
        self.position_absolute(self.episode_label, 0, 20, 20, 5)
        self.position_absolute(self.episode, 20, 20, 20, 5)

        self.search_label = self.generate_label("Search Term")
        self.search_field = self.generate_text_entry("", self.search_xdcc)
        self.position_absolute(self.search_label, 0, 30, 20, 5)
        self.position_absolute(self.search_field, 20, 30, 20, 5)

        self.search_engine_label = self.generate_label("Search Engine")
        self.search_engine_combo_box = self.generate_string_combo_box(SearchEngineManager.get_search_engine_strings())
        self.position_absolute(self.search_engine_label, 0, 35, 20, 5)
        self.position_absolute(self.search_engine_combo_box, 20, 35, 20, 5)

        self.search_button = self.generate_button("Start Search", self.search_xdcc)
        self.position_absolute(self.search_button, 0, 45, 40, 5)

        # Icon Information
        self.main_icon_label = self.generate_label("Main Icon")
        self.secondary_icon_label = self.generate_label("Season Icon")
        self.main_icon_location = self.generate_text_entry("")
        self.secondary_icon_location = self.generate_text_entry("")
        self.method_label = self.generate_label("Method")
        self.method_combo_box = self.generate_string_combo_box(DeepIconizer.get_iconizer_options())
        self.position_absolute(self.main_icon_label, 0, 55, 20, 5)
        self.position_absolute(self.secondary_icon_label, 0, 60, 20, 5)
        self.position_absolute(self.main_icon_location, 20, 55, 20, 5)
        self.position_absolute(self.secondary_icon_location, 20, 60, 20, 5)
        self.position_absolute(self.method_label, 0, 65, 20, 5)
        self.position_absolute(self.method_combo_box, 20, 65, 20, 5)

        # Multi List Boxes
        self.search_results_label = self.generate_label("Search Results")
        self.directory_content_label = self.generate_label("Episodes")
        self.position_absolute(self.search_results_label, 50, 0, 60, 5)
        self.position_absolute(self.directory_content_label, 120, 0, 20, 5)

        self.search_results = self.generate_primitive_multi_column_list_box(
            {"#": (0, int), "Bot": (1, str), "Pack": (2, int), "Size": (3, str), "Filename": (4, str)})
        self.position_absolute(self.search_results, 50, 5, 70, 40)

        self.directory_content = self.generate_primitive_multi_column_list_box({"File Name": (0, str)})
        self.position_absolute(self.directory_content, 120, 5, 30, 40)

        # Download Section
        self.rename_check = self.generate_check_box("Automatic Rename", True)
        self.position_absolute(self.rename_check, 80, 45, 30, 12)

        self.download_engine_label = self.generate_label("Download Engine")
        self.download_engine_combo_box = self.generate_string_combo_box(DownloaderManager.get_downloader_strings("all"))
        self.position_absolute(self.download_engine_label, 80, 57, 15, 13)
        self.position_absolute(self.download_engine_combo_box, 95, 57, 15, 13)

        self.download_button = self.generate_button("Start Download", self.start_download)
        self.position_absolute(self.download_button, 50, 45, 30, 25)

        self.total_progress_bar = self.generate_percentage_progress_bar()
        self.total_progress_label = self.generate_label("Total Progress")
        self.total_progress_current = self.generate_label("")
        self.total_progress_total = self.generate_label("")
        self.single_progress_bar = self.generate_percentage_progress_bar()
        self.single_progress_label = self.generate_label("Single Progress")
        self.single_progress_current = self.generate_label("")
        self.single_progress_total = self.generate_label("")
        self.download_speed = self.generate_label("-")
        self.download_speed_label = self.generate_label("Download Speed")
        self.average_dl_speed = self.generate_label("-")
        self.average_dl_speed_label = self.generate_label("Average Speed")
        self.time_left = self.generate_label("-")
        self.time_left_label = self.generate_label("Time Left")
        self.position_absolute(self.total_progress_bar, 128, 45, 19, 5)
        self.position_absolute(self.total_progress_label, 110, 45, 15, 5)
        self.position_absolute(self.total_progress_current, 125, 45, 3, 5)
        self.position_absolute(self.total_progress_total, 147, 45, 3, 5)
        self.position_absolute(self.single_progress_bar, 128, 50, 19, 5)
        self.position_absolute(self.single_progress_label, 110, 50, 15, 5)
        self.position_absolute(self.single_progress_current, 125, 50, 3, 5)
        self.position_absolute(self.single_progress_total, 147, 50, 3, 5)
        self.position_absolute(self.download_speed, 128, 55, 19, 5)
        self.position_absolute(self.download_speed_label, 110, 55, 15, 5)
        self.position_absolute(self.average_dl_speed, 128, 60, 19, 5)
        self.position_absolute(self.average_dl_speed_label, 110, 60, 15, 5)
        self.position_absolute(self.time_left, 128, 65, 19, 5)
        self.position_absolute(self.time_left_label, 110, 65, 15, 5)

    def search_xdcc(self, widget: object) -> None:
        """
        Searches for xdcc packs using the currently selected search engine and search term, using a separate thread.
        If a search is already running, it won't start a new search.

        :param widget: the search button
        :return: None
        """
        # Widget is not None syntax used to shut up the IDE
        # Do not start a search if a search is already in progress or a download is currently running
        if widget is None or self.searching or self.search_thread is not None or self.dl_progress is not None:
            return

        def search() -> None:
            """
            Conducts the actual search using the selected search engine

            :return: None
            """
            # Sets the searching flag to True, letting other parts of the program know about it
            self.searching = True
            # Set the text of the search button to "Searching..." in a threads safe way
            self.run_thread_safe(self.set_button_string, (self.search_button, "Searching..."))

            # Get the selected search engine from the search engine combo box
            search_engine = self.get_string_from_current_selected_combo_box_option(self.search_engine_combo_box)
            # Get the search term from the search term text entry
            search_term = self.get_string_from_text_entry(self.search_field)
            # Conduct the search and save the list of results to the search_result variable
            self.search_result = BatchDownloadManager.conduct_xdcc_search(search_engine, search_term)

        def search_xdcc_thread() -> None:
            """
            Updates the GUI elements with the search results. This requires this to be handled in a way that
            doesn't threaten the GUI's integrity, which means that this method must be run as a sensitive thread
            using gfworks' threading capabilities

            :return: None
            """
            self.clear_primitive_multi_list_box(self.search_results)  # Clear the search results listbox

            # Add the search results to the listbox
            i = 0
            for result in self.search_result:
                choice = (i,) + result.to_tuple()
                self.add_primitive_multi_list_box_element(self.search_results, choice)
                i += 1

            # Reset the Search Button to display "Start Search"
            self.run_thread_safe(self.set_button_string, (self.search_button, "Start Search"))
            self.searching = False  # Reset the searching flag
            self.search_thread = None  # Clear the search_thread variable to enable a new search

        # Run the two defined methods in a thread-safe manner.
        # The insensitive target is executed before the sensitive target
        self.search_thread = self.run_sensitive_thread_in_parallel(target=search_xdcc_thread, insensitive_target=search)

    def start_download(self, widget):
        """
        Starts the Download
        :param widget: the Download Button
        :return: void
        """

        # Widget is not None syntax used to shut up the IDE
        # Do not start a download if a search is currently in progress or a download is currently running
        if widget is None or self.searching or self.search_thread is not None or self.dl_progress is not None:
            return

        # Define local method that handles progress updating
        def update_progress_thread(progress_struct: ProgressStruct) -> None:
            """
            Updates the progress UI elements

            :param progress_struct: the progress structure to be displayed
            :return: None
            """
            def complete_dl() -> None:
                """
                Run when the download has completed, rests all progress UI elements to their default state

                :return: None
                """
                self.set_button_string(self.download_button, "Download")  # Reset Download button text
                self.reset_percentage_progress_bar(self.single_progress_bar)  # Set progress bar to 0.0
                self.reset_percentage_progress_bar(self.total_progress_bar)  # Set progress bar to 0.0
                self.set_label_string(self.download_speed, "-")  # Sets the download speed label to '-'
                # Clear all progress labels
                self.clear_label_text(self.total_progress_current)
                self.clear_label_text(self.total_progress_total)
                self.clear_label_text(self.single_progress_current)
                self.clear_label_text(self.single_progress_total)
                self.clear_label_text(self.average_dl_speed)
                self.clear_label_text(self.time_left)

                # Force a directory content update for the new directory content to be displayed by the
                # Directory Content List Box
                self.on_directory_changed(1)

            def update() -> None:
                """
                Updates the widgets with new values

                :return: None
                """
                # calculate the progress values
                try:
                    single_progress = float(progress_struct.single_progress) / float(progress_struct.single_size)
                except ZeroDivisionError:
                    single_progress = 0.0
                total_progress = float(progress_struct.total_progress) / float(progress_struct.total)
                total_progress_percentage = total_progress + (single_progress / progress_struct.total)

                # update the UI elements
                self.set_progress_bar_float_percentage(self.total_progress_bar, total_progress_percentage)
                self.set_progress_bar_float_percentage(self.single_progress_bar, single_progress)
                self.set_label_string(self.total_progress_current, str(progress_struct.total_progress))
                self.set_label_string(self.total_progress_total, str(progress_struct.total))
                self.set_label_string(self.single_progress_current, str(progress_struct.single_progress))
                self.set_label_string(self.single_progress_total, str(progress_struct.single_size))

            # Set local variables to store information gathered over multiple loops
            last_single_progress_size = 0.0  # Stores the last recorded size of the downloaded file
            speed_time_counter = 0  # Seconds since last download size change
            total_time_counter = 0  # Seconds since download start
            finished_download_amount = 0.0  # Total downloaded so far

            while True:

                # Update the progress UI elements
                self.run_thread_safe(update)

                # Calculate download speeds if the progress has changed
                if float(progress_struct.single_progress) != last_single_progress_size:

                    # Once we get to the new file, add previous file size to finished_download_amount
                    if last_single_progress_size > float(progress_struct.single_progress):
                        finished_download_amount += last_single_progress_size

                    # calculate the current-ish speed using the current size and the previous size
                    # If it's a negative number, reset it to 0.
                    speed = (float(progress_struct.single_progress) - last_single_progress_size) / speed_time_counter
                    if speed < 0:
                        speed = 0

                    # Reset the speed time counter
                    speed_time_counter = 0
                    # Store the current downloaded size as variable
                    last_single_progress_size = float(progress_struct.single_progress)

                    # Calculate average speed
                    total_down = (float(progress_struct.single_progress) + finished_download_amount)
                    average_speed = int(total_down / total_time_counter)
                    time_left = int(progress_struct.single_size / average_speed)

                    # Update Speed Labels
                    self.run_thread_safe(self.set_label_string, (self.download_speed, str(int(speed)) + " Byte/s"))
                    self.run_thread_safe(self.set_label_string, (self.average_dl_speed, str(average_speed) + " Byte/s"))
                    self.run_thread_safe(self.set_label_string, (self.time_left, str(time_left) + "s"))

                # If all downloads complete, stop updating progress, reset progress UI elements,
                # Allow new downloads
                if progress_struct.total == progress_struct.total_progress:
                    self.run_thread_safe(complete_dl)  # Resets all progress-related UI elements
                    self.dl_progress = None  # Clear dl_progress variable to enable new download processes
                    break  # Break out of the endless loop

                # Increment time counters, then pause for 1 second
                speed_time_counter += 1
                total_time_counter += 1
                time.sleep(1)

        # Prepare the download, also performs validity checks
        preparation = BatchDownloadManager.prepare(self.get_string_from_text_entry(self.destination),
                                                   self.get_string_from_text_entry(self.show),
                                                   self.get_string_from_text_entry(self.season),
                                                   self.get_string_from_text_entry(self.episode),
                                                   self.get_string_from_text_entry(self.main_icon_location),
                                                   self.get_string_from_text_entry(self.secondary_icon_location),
                                                   self.get_string_from_current_selected_combo_box_option(
                                                       self.method_combo_box))

        # If errors occur while preparing the download, stop the download process and notify the user of the
        # exact cause.
        if len(preparation) != 6:  # Preparation returns 2-part tuple if unsuccessful, otherwise 6-part tuple
            self.show_message_dialog(preparation["error_title"], preparation["error_text"])
            return  # Stop download process

        # Get selected packs from the search result List Box
        selected_packs = self.get_list_of_selected_elements_from_multi_list_box(self.search_results)
        packs = []  # Store XDCCPack objects in list
        for selection in selected_packs:
            packs.append(self.search_result[selection[0]])
        if len(packs) == 0:
            return  # If no packs are selected abort the download process

        # Set the button text of the Download button to display "Downloading..." to let the user know that
        # a download is currently running
        self.set_button_string(self.download_button, "Downloading...")

        # Get selected downloader type from Combo Box
        downloader = self.get_string_from_current_selected_combo_box_option(self.download_engine_combo_box)

        # Set up progress structure
        progress = ProgressStruct()
        progress.total = len(packs)

        # Start the update thread
        self.run_thread_in_parallel(target=update_progress_thread, args=(progress,))

        # Start the download thread
        self.run_thread_in_parallel(target=BatchDownloadManager.start_download_process,
                                    args=(preparation, downloader, packs,
                                          self.get_boolean_from_check_box(self.rename_check), progress))

        # Set the class variable dl_progress to point to the progress structure to disable
        # additional concurrent downloads
        self.dl_progress = progress

    def on_directory_changed(self, widget: object) -> None:
        """
        Method run when the directory Entry text changes

        It automatically browses through the specified directory in search of relevant information, like
        show name, season number, first episode number, directory content etc.

        :param widget: the changed text entry
        :return: None
        """
        # Should not happen, just used to shut up IDE warnings about unused variables
        if widget is None:
            return

        # Get the currently entered directory
        directory = self.get_string_from_text_entry(self.destination)

        show_name, season, episode, main_icon, secondary_icon = BatchDownloadManager.analyse_show_directory(directory)

        # Set the GUI elements to the calculated values
        self.set_text_entry_string(self.show, show_name)
        self.set_text_entry_string(self.search_field, show_name)
        self.set_text_entry_string(self.episode, episode)
        self.set_text_entry_string(self.season, season)
        self.set_text_entry_string(self.main_icon_location, main_icon)
        self.set_text_entry_string(self.secondary_icon_location, secondary_icon)

        # Clear the directory content list box
        self.clear_primitive_multi_list_box(self.directory_content)

        # Fill the directory content list box, if the directory has a season subdirectory
        season_directory = os.path.join(directory, "Season " + season)
        if os.path.isdir(season_directory):
            season_directory_content = os.listdir(season_directory)
            for element in season_directory_content:
                self.add_primitive_multi_list_box_element(self.directory_content, (element,))

    def browse_for_destination(self, widget: object) -> None:
        """
        Opens a file browser dialog to select a directory to the show's root directory

        :param widget: the button that caused this method call
        :return: None
        """
        # used to trick IDE warnings
        if widget is not None:
            directory = self.show_directory_chooser_dialog()  # Show a directory chooser dialog
            self.set_text_entry_string(self.destination, directory)  # and then set the entry text to the result
