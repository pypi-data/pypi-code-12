"""bsw page model and functions"""

import os
import re

from . import templates
from . import includes


class Page:
    def __init__(self, filename):
        self.filename = filename
        self.body = None  # The page body after var replacement
        self.body_raw = None  # The un-transformed page body
        self.rendered_page = None  # Finished page rendered with template
        self.page_vars = {}

    def load_and_parse(self):
        self.load()
        self.extract_vars()
        self.strip_vars()

    def load(self):
        """Load page from file."""
        with open(os.path.join("pages", self.filename), "r") as page_file:
            self.body_raw = page_file.read()

    def extract_vars(self):
        """Populate self.vars with vars extracted from page."""
        regex_var_capture = "<!--\s+(\w+)\s+=\s+\"([^>]*)\"\s+-->"
        matches = re.findall(regex_var_capture, self.body_raw)
        for match in matches:
            self.page_vars[match[0]] = match[1]

    def strip_vars(self):
        """Strip page vars from raw body and populate self.body."""
        page_data = self.body_raw
        for page_var in self.page_vars:
            regex_this_var = "<!--\s+({0})\s+=\s+\"({1})\"\s+-->".format(
                                page_var,
                                self.page_vars[page_var])
            page_data = re.sub(regex_this_var, "", page_data)
        self.body = page_data

    def replace_includes(self):
        """Replace <!-- include("my_include.html") --> directives with the
        referenced file.
        """
        regex_include = "<!--\s+include\(\"([^>]*)\"\)\s+-->"
        matches = re.findall(regex_include, self.body)
        for match in matches:
            include_data = includes.get_include(match)
            regex_this_include = "<!--\s+include\(\"{0}\"\)\s+-->".format(match)
            self.rendered_page = re.sub(regex_this_include,
                                        include_data,
                                        self.body)

    def render(self):
        """Render page using template, insert any includes and do page
        var replacement.
        """
        if "template" in self.page_vars:
            template = templates.get_template(self.page_vars["template"])
        else:
            template = templates.get_template("base.html")

        self.rendered_page = template.replace("$page_content", self.body)
        self.replace_includes()
        for page_var in self.page_vars:
            self.rendered_page = self.rendered_page.replace("$" + page_var,
                                                            self.page_vars[page_var])


def collect_pages():
    """Collect source page from "pages" folder in pwd"""
    page_paths = []
    pages = []

    for (dirpath, dirnames, filenames) in os.walk("pages/"):
        for filename in filenames:
            if filename.endswith(".html") or filename.endswith(".htm"):
                page_paths.append(
                    os.path.join(dirpath, filename).split(
                                    os.path.sep, 1)[1])

    for page_path in page_paths:
        new_page = Page(page_path)
        pages.append(new_page)

    return pages


def write_pages(pages, out_dir):
    """Write rendered page to out_dir"""
    for page in pages:
        if not os.path.isdir(
                os.path.join(out_dir, os.path.dirname(page.filename))):
            os.makedirs(os.path.join(out_dir, os.path.dirname(page.filename)))
        with open(os.path.join(out_dir, page.filename), "w") as out_file:
            out_file.write(page.rendered_page)
