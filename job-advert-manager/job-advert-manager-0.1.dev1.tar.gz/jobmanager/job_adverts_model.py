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

import json

JSON_FILENAME = "job_adverts.json"

class JobAdvertsModel(object):

    def __init__(self):

        # Load the JSON database
        self.json_database = {"job_adverts": {}, "job_searchs": {}}
        try:
            fd = open(JSON_FILENAME, "r")
            self.json_database = json.load(fd)
            fd.close()
        except FileNotFoundError:
            pass


        # Creating the gtk.ListStore model
        self.liststore = gtk.ListStore(str, str, str, str, int, str, str)
        for url, job_advert_dict in self.json_database["job_adverts"].items():
            tooltip = url.replace('&', '&amp;')
            category = job_advert_dict["category"]
            organization = job_advert_dict["organization"]
            score = job_advert_dict["score"]
            title = job_advert_dict["title"]
            date = job_advert_dict["date"]

            self.liststore.append([url, tooltip, category, organization, score, date, title])


    def get_json_filename(self):
        return JSON_FILENAME


    def save_json_file(self):
        # Save the JSON file
        with open(self.get_json_filename(), "w") as fd:
            json.dump(self.json_database, fd, sort_keys=True, indent=4)

