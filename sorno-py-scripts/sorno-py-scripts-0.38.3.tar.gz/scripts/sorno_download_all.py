#!/usr/bin/env python
"""Downloads all items from all links from a URL.

Usually, you want to use --regex to filter out what you need. Using --dry-out
to tune your regex before the actual downloading of course.

Example:

    Let say there is a webpage with url http://content.com that has a lot of
    links to http://good-stuff/stuff1.zip, http://good-stuff/stuff2.zip, etc.
    You should do this first to see if you get all the links you want:

        sorno_download_all.py --dry-run --regex "stuff.*zip" \\
            "http://content.com"

    Then run the actual command to download them.

        sorno_download_all.py --regex "stuff.*zip" "http://content.com"


    Copyright 2014 Heung Ming Tai

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import argparse
import logging
import os
import re
import sys

from lxml import html
import requests
from sorno import webutil
from sorno import loggingutil


_LOG = logging.getLogger(__name__)
_PLAIN_LOGGER = None  # will be created in main()


class DownloadAllApp(object):
    def __init__(
        self,
        url,
        regex,
        out_dir,
        dry_run=False,
    ):
        self.url = url
        self.regex = re.compile(regex)
        self.out_dir = out_dir
        self.dry_run = dry_run

    def run(self):
        _LOG.info("Fetch links from url: %s", self.url)
        header = {
            # most common user-agent
            'user-agent': 'Mozilla/5.0 ;Windows NT 6.1; WOW64; Trident/7.0; rv:11.0; like Gecko',
        }
        page = requests.get(self.url, headers=header)
        tree = html.fromstring(page.text)
        tree.make_links_absolute(self.url, resolve_base_href=True)

        elements_links = []
        for element, attribute, link, pos in tree.iterlinks():
            if self.regex.search(link):
                elements_links.append((element, link))
            else:
                _LOG.debug("Skip [%s]", link)

        num_links = len(elements_links)
        for i, (element, link) in enumerate(elements_links):
            if self.regex.search(link):
                _LOG.info(
                    "(%s/%s) %s (%s)",
                    i + 1,
                    num_links,
                    element.text,
                    link,
                )
                new_filepath = os.path.join(
                    self.out_dir,
                    webutil.unquote_url(os.path.basename(link)),
                )

                if os.path.exists(new_filepath):
                    _LOG.info(
                        "Skip [%s] since [%s] already exists",
                        link,
                        new_filepath,
                    )
                    continue
                _LOG.info("Download to [%s]", new_filepath)
                if not self.dry_run:
                    tmp_filepath = new_filepath + ".tmp"
                    webutil.download_file(link, tmp_filepath)
                    os.rename(tmp_filepath, new_filepath)


def parse_args(cmd_args):
    description = """
        Downloads all items from all links from a URL.
    """
    parser = argparse.ArgumentParser(
        description=description,
    )
    parser.add_argument(
        "--debug",
        action="store_true",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
    )
    parser.add_argument(
        "--out-dir",
        help="The directory to store downloaded files,"
            + " default to \"%(default)s\".",
        default=".",
    )
    parser.add_argument(
        "--regex",
        default=".*",
        help="Only download links with matched regex",
    )
    parser.add_argument("url")

    args = parser.parse_args(cmd_args)
    return args


def main():
    global _PLAIN_LOGGER

    args = parse_args(sys.argv[1:])

    loggingutil.setup_logger(_LOG, debug=args.debug)
    _PLAIN_LOGGER = loggingutil.create_plain_logger("PLAIN")

    app = DownloadAllApp(
        args.url,
        args.regex,
        args.out_dir,
        dry_run=args.dry_run,
    )
    app.run()


if __name__ == '__main__':
    main()
