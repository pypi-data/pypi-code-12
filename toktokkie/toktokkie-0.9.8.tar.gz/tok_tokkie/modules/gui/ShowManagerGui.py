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
from tok_tokkie.metadata import Globals


class ShowManagerGui(Globals.selected_grid_gui_framework):
    """
    GUI for the Show Manager plugin
    """

    def __init__(self, parent: Globals.selected_grid_gui_framework) -> None:
        """
        Constructor
        :param parent: the parent gui
        :return: void
        """
        # Initialization
        self.directory_browse_entry = None
        self.directory_browse_button = None
        self.directory_name_label = None
        self.directory_content_list_box = None

        self.selected_show_name = None
        self.selected_show_main_icon = None
        self.selected_show_season_icon = None
        self.selected_show_content_list_box = None

        super().__init__("Show Manager", parent, True)

    def lay_out(self) -> None:
        """
        Sets up all interface elements of the GUI
        :return: void
        """
        self.directory_browse_entry = self.generate_text_entry("")
        self.directory_browse_button = self.generate_button("Browse")
        self.directory_name_label = self.generate_label("                                    ")
        self.directory_content_list_box = self.generate_primitive_multi_column_list_box(
            {"Directory": (0, str), "Show Name": (1, str)}, False)

        self.position_absolute(self.directory_browse_entry, 0, 0, 10, 5)
        self.position_absolute(self.directory_browse_button, 10, 0, 10, 5)
        self.position_absolute(self.directory_name_label, 20, 0, 10, 5)
        self.position_absolute(self.directory_content_list_box, 0, 5, 30, 50)

        self.selected_show_name = self.generate_label("")
        self.selected_show_main_icon = self.generate_label("Image goes Here")
        self.selected_show_season_icon = self.generate_label("Image goes Here")
        self.selected_show_content_list_box = self.generate_primitive_multi_column_list_box({"Show Name": (0, str)})

        self.position_absolute(self.selected_show_name, 30, 0, 40, 10)
        self.position_absolute(self.selected_show_main_icon, 30, 10, 20, 20)
        self.position_absolute(self.selected_show_season_icon, 50, 10, 20, 20)
        self.position_absolute(self.selected_show_content_list_box, 30, 30, 40, 25)




