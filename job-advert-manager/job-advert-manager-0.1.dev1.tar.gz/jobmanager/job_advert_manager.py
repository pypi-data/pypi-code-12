#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2015 Jérémie DECOCK (http://www.jdhp.org)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
...
"""

from gi.repository import Gtk as gtk

import fcntl  # TODO: use GtkApplication instead
import sys

import add_and_edit_container
import job_adverts_model
import job_adverts_view
import search_container
import stats_container

LOCK_FILENAME = ".lock"  # TODO: use GtkApplication instead

class MainWindow(gtk.Window):

    def __init__(self):

        self.job_adverts_model = job_adverts_model.JobAdvertsModel()

        # Build the main window
        gtk.Window.__init__(self, title="Job advert logger")
        self.maximize()
        self.set_border_width(4)

        notebook_container = gtk.Notebook()
        self.add(notebook_container)

        # Add job advert container ############################################

        self.add_container = add_and_edit_container.AddAndEditContainer(self, self.job_adverts_model, edit_mode=False)

        # Edit container ######################################################

        # Treeview
        self.job_advert_treeview = job_adverts_view.JobAdvertsView(self.job_adverts_model.liststore, None) # TODO!!!

        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_border_width(18)
        scrolled_window.set_shadow_type(gtk.ShadowType.IN)
        scrolled_window.set_policy(gtk.PolicyType.AUTOMATIC, gtk.PolicyType.ALWAYS)
        scrolled_window.add(self.job_advert_treeview)

        # Edit box container
        self.edit_container = add_and_edit_container.AddAndEditContainer(self, self.job_adverts_model, edit_mode=True, treeview=self.job_advert_treeview)
        self.job_advert_treeview.edit_container = self.edit_container # TODO!!!

        # Add the widgets to the container
        paned_container = gtk.Paned(orientation=gtk.Orientation.VERTICAL)
        paned_container.add1(scrolled_window)
        paned_container.add2(self.edit_container)

        # The position in pixels of the divider (i.e. the default size of the top pane)
        paned_container.set_position(400)

        # Job search container ################################################

        search_job_adverts_container = search_container.SearchContainer(self.job_adverts_model)

        # Stats container #####################################################

        stats_job_adverts_container = stats_container.StatsContainer(self.job_adverts_model)

        ###################################

        add_label = gtk.Label(label="Add")
        notebook_container.append_page(self.add_container, add_label)

        edit_label = gtk.Label(label="Edit")
        notebook_container.append_page(paned_container, edit_label)

        search_label = gtk.Label(label="Search")
        notebook_container.append_page(search_job_adverts_container, search_label)

        stats_label = gtk.Label(label="Stats")
        notebook_container.append_page(stats_job_adverts_container, stats_label)


def main():

    # Acquire an exclusive lock on LOCK_FILENAME
    fd = open(LOCK_FILENAME, "w")  # TODO: use GtkApplication instead

    try:  # TODO: use GtkApplication instead
        # LOCK_EX = acquire an exclusive lock on fd
        # LOCK_NB = make a nonblocking request
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)  # TODO: use GtkApplication instead

        ###################################

        window = MainWindow()

        window.connect("delete-event", gtk.main_quit) # ask to quit the application when the close button is clicked
        window.show_all()                             # display the window
        gtk.main()                                    # GTK+ main loop

        ###################################

        # LOCK_UN = unlock fd
        fcntl.flock(fd, fcntl.LOCK_UN)  # TODO: use GtkApplication instead
    except IOError:  # TODO: use GtkApplication instead
        #print(LOCK_FILENAME + " is locked ; another instance is running. Exit.")
        dialog = gtk.MessageDialog(parent=None, flags=0, message_type=gtk.MessageType.ERROR, buttons=gtk.ButtonsType.OK, message_format="Another instance is running in the same directory")
        dialog.format_secondary_text("Exit.")
        dialog.run()
        dialog.destroy()

        sys.exit(1)


if __name__ == '__main__':
    main()

