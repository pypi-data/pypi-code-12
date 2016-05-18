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

from gi.repository import Gtk as gtk

import datetime
import json

import category_list

DEFAULT_SCORE = 5

class AddAndEditContainer(gtk.Grid):

    def __init__(self, main_window, job_adverts_model, edit_mode=False, treeview=None):
        """
        ...
        """

        super(AddAndEditContainer, self).__init__()

        self.main_window = main_window
        self.job_adverts_model = job_adverts_model

        self.edit_mode = edit_mode
        self.treeview = treeview

        self.category_combobox = gtk.ComboBoxText()
        self.organization_entry = gtk.Entry()
        self.url_entry = gtk.Entry()

        if self.edit_mode:
            self.url_entry.set_editable(False)

        self.title_entry = gtk.Entry()
        self.score_spin_button = gtk.SpinButton()
        self.pros_textview = gtk.TextView()
        self.cons_textview = gtk.TextView()
        self.desc_textview = gtk.TextView()

        # Category
        category_label = gtk.Label(label="Category")

        self.category_combobox.set_entry_text_column(0)
        for category in category_list.CATEGORY_LIST:
            self.category_combobox.append_text(category)
        self.category_combobox.set_active(-1)    # -1 = no active item selected

        # Organization
        organization_label = gtk.Label(label="Organization")

        # URL
        url_label = gtk.Label(label="Url")

        # Title
        title_label = gtk.Label(label="Title")

        # Score
        score_label = gtk.Label(label="Score")

        self.score_spin_button.set_increments(step=1, page=5)
        self.score_spin_button.set_range(min=0, max=5)
        self.score_spin_button.set_value(5)
        self.score_spin_button.set_numeric(True)
        self.score_spin_button.set_update_policy(gtk.SpinButtonUpdatePolicy.IF_VALID)

        # Pros
        pros_label = gtk.Label(label="Pros")

        self.pros_textview.set_wrap_mode(gtk.WrapMode.WORD)

        pros_scrolled_window = gtk.ScrolledWindow()
        pros_scrolled_window.set_border_width(3)
        pros_scrolled_window.set_shadow_type(gtk.ShadowType.OUT)
        pros_scrolled_window.set_policy(gtk.PolicyType.AUTOMATIC, gtk.PolicyType.ALWAYS)
        pros_scrolled_window.add(self.pros_textview)

        # Cons
        cons_label = gtk.Label(label="Cons")

        self.cons_textview.set_wrap_mode(gtk.WrapMode.WORD)

        cons_scrolled_window = gtk.ScrolledWindow()
        cons_scrolled_window.set_border_width(3)
        cons_scrolled_window.set_shadow_type(gtk.ShadowType.OUT)
        cons_scrolled_window.set_policy(gtk.PolicyType.AUTOMATIC, gtk.PolicyType.ALWAYS)
        cons_scrolled_window.add(self.cons_textview)

        # Description
        desc_label = gtk.Label(label="Description")

        self.desc_textview.set_wrap_mode(gtk.WrapMode.WORD)

        desc_scrolled_window = gtk.ScrolledWindow()
        desc_scrolled_window.set_border_width(3)
        desc_scrolled_window.set_shadow_type(gtk.ShadowType.OUT)
        desc_scrolled_window.set_policy(gtk.PolicyType.AUTOMATIC, gtk.PolicyType.ALWAYS)
        desc_scrolled_window.add(self.desc_textview)

        # Buttons
        add_button = gtk.Button(label="Save")
        add_button.connect("clicked", self.saveCallBack)

        cancel_button = gtk.Button(label="Cancel")
        cancel_button.connect("clicked", self.clearCallBack)

        # The grid container
        self.set_column_homogeneous(False)
        self.set_row_homogeneous(False)
        self.set_column_spacing(12)
        self.set_row_spacing(6)
        self.set_border_width(18)

        # Set hexpand, vexpand, halign, valign
        # See https://developer.gnome.org/gtk3/stable/ch29s02.html
        self.category_combobox.set_hexpand(True)

        self.organization_entry.set_hexpand(True)

        self.url_entry.set_hexpand(True)

        self.score_spin_button.set_hexpand(True)

        self.title_entry.set_hexpand(True)

        pros_scrolled_window.set_hexpand(True)
        pros_scrolled_window.set_vexpand(True)

        cons_scrolled_window.set_hexpand(True)
        cons_scrolled_window.set_vexpand(True)
        
        desc_scrolled_window.set_hexpand(True)
        desc_scrolled_window.set_vexpand(True)

        # Align labels to the right
        # See https://developer.gnome.org/gtk3/stable/ch29s02.html
        category_label.set_halign(gtk.Align.END)
        organization_label.set_halign(gtk.Align.END)
        url_label.set_halign(gtk.Align.END)
        score_label.set_halign(gtk.Align.END)
        title_label.set_halign(gtk.Align.END)

        # Align labels to the left
        # See https://developer.gnome.org/gtk3/stable/ch29s02.html
        pros_label.set_halign(gtk.Align.START)
        cons_label.set_halign(gtk.Align.START)
        desc_label.set_halign(gtk.Align.START)

        # Add the widgets to the container
        self.attach(title_label,             left=0, top=0, width=1, height=1)
        self.attach(self.title_entry,        left=1, top=0, width=3, height=1)

        self.attach(category_label,          left=0, top=1, width=1, height=1)
        self.attach(self.category_combobox,  left=1, top=1, width=1, height=1)
        self.attach(organization_label,      left=2, top=1, width=1, height=1)
        self.attach(self.organization_entry, left=3, top=1, width=1, height=1)

        self.attach(url_label,               left=0, top=2, width=1, height=1)
        self.attach(self.url_entry,          left=1, top=2, width=1, height=1)
        self.attach(score_label,             left=2, top=2, width=1, height=1)
        self.attach(self.score_spin_button,  left=3, top=2, width=1, height=1)

        self.attach(pros_label,              left=0, top=3, width=2, height=1)
        self.attach(cons_label,              left=2, top=3, width=2, height=1)

        self.attach(pros_scrolled_window,    left=0, top=4, width=2, height=1)
        self.attach(cons_scrolled_window,    left=2, top=4, width=2, height=1)

        self.attach(desc_label,              left=0, top=5, width=4, height=1)

        self.attach(desc_scrolled_window,    left=0, top=6, width=4, height=6)

        self.attach(add_button,              left=0, top=13, width=2, height=1)
        self.attach(cancel_button,           left=2, top=13, width=2, height=1)


    def saveCallBack(self, widget):
        """
        Save the current job advert.
        """

        # Get data from entry widgets ###########

        category = self.category_combobox.get_active_text()

        organization = self.organization_entry.get_text()

        url = self.url_entry.get_text()
        tooltip = url.replace('&', '&amp;')

        title = self.title_entry.get_text()

        score = self.score_spin_button.get_value_as_int()

        pros_buffer = self.pros_textview.get_buffer()
        pros = pros_buffer.get_text(pros_buffer.get_start_iter(), pros_buffer.get_end_iter(), True)

        cons_buffer = self.cons_textview.get_buffer()
        cons = cons_buffer.get_text(cons_buffer.get_start_iter(), cons_buffer.get_end_iter(), True)

        desc_buffer = self.desc_textview.get_buffer()
        desc = desc_buffer.get_text(desc_buffer.get_start_iter(), desc_buffer.get_end_iter(), True)

        if self.edit_mode:
            date = self.job_adverts_model.json_database["job_adverts"][url]["date"]
        else:
            date = datetime.date.isoformat(datetime.date.today())

        # Check data ############################

        error_msg_list = []

        if category is None:
            error_msg_list.append("You must select a category.")

        if len(url) == 0:
            error_msg_list.append("You must enter an url.")
        elif url in self.job_adverts_model.json_database["job_adverts"] and not self.edit_mode:
            error_msg_list.append("This job advert already exists in the database.")

        try:
            if score not in range(6):
                error_msg_list.append("The score must be a number between 0 and 5.")
        except:
            error_msg_list.append("The score must be a number between 0 and 5.")

        # Save data or display error ############

        if len(error_msg_list) == 0:
            job_advert_dict = {"date": date,
                               "category": category,
                               "organization": organization,
                               "title": title,
                               "score": score,
                               "pros": pros,
                               "cons": cons,
                               "desc": desc}

            # Save the job advert in the database
            self.job_adverts_model.json_database["job_adverts"][url] = job_advert_dict

            # Save the job advert in the JSON file
            self.job_adverts_model.save_json_file()

            # Update the GtkListStore (TODO: redundant with the previous JSON data structure)
            if self.edit_mode:
                model, treeiter = self.treeview.get_selection().get_selected()
                self.job_adverts_model.liststore.set_value(treeiter, 2, category)      # category
                self.job_adverts_model.liststore.set_value(treeiter, 3, organization)  # organization
                self.job_adverts_model.liststore.set_value(treeiter, 4, score)         # score
                self.job_adverts_model.liststore.set_value(treeiter, 6, title)         # title
            else:
                self.job_adverts_model.liststore.append([url, tooltip, category, organization, score, date, title])

            # Clear all entries
            self.clearCallBack()
        else:
            dialog = gtk.MessageDialog(self.main_window, 0, gtk.MessageType.ERROR, gtk.ButtonsType.OK, "Error")
            dialog.format_secondary_text("\n".join(error_msg_list))
            dialog.run()
            dialog.destroy()


    def clearCallBack(self, widget=None, data=None):
        if self.edit_mode:
            # Clear the current form: reset the entry widgets to their default value.

            model, treeiter = self.treeview.get_selection().get_selected()
            url = None
            if treeiter != None:
                url = self.job_adverts_model.liststore[treeiter][0]

            if url is None:
                self.url_entry.set_text("")
                self.category_combobox.set_active(-1) # -1 = no active item selected
                self.organization_entry.set_text("")
                self.score_spin_button.set_value(0)
                self.title_entry.set_text("")
                self.pros_textview.get_buffer().set_text("")
                self.cons_textview.get_buffer().set_text("")
                self.desc_textview.get_buffer().set_text("")
            else:
                category = self.job_adverts_model.json_database["job_adverts"][url]["category"]
                organization = self.job_adverts_model.json_database["job_adverts"][url]["organization"]
                score = self.job_adverts_model.json_database["job_adverts"][url]["score"]
                title = self.job_adverts_model.json_database["job_adverts"][url]["title"]
                pros = self.job_adverts_model.json_database["job_adverts"][url]["pros"]
                cons = self.job_adverts_model.json_database["job_adverts"][url]["cons"]
                desc = self.job_adverts_model.json_database["job_adverts"][url]["desc"]

                self.url_entry.set_text(url)
                self.category_combobox.set_active(category_list.CATEGORY_LIST.index(category))
                self.organization_entry.set_text(organization)
                self.score_spin_button.set_value(score)
                self.title_entry.set_text(title)
                self.pros_textview.get_buffer().set_text(pros)
                self.cons_textview.get_buffer().set_text(cons)
                self.desc_textview.get_buffer().set_text(desc)
        else:
            # Clear all entries except "category_combobox" and "organization_entry"
            self.url_entry.set_text("")
            #self.organization_entry.set_text("")
            self.title_entry.set_text("")
            self.score_spin_button.set_value(DEFAULT_SCORE)
            self.pros_textview.get_buffer().set_text("")
            self.cons_textview.get_buffer().set_text("")
            self.desc_textview.get_buffer().set_text("")

