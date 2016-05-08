#!/usr/bin/env python
"""Downloads podcasts given a feed url.

The downloaded podcasts have useful file names (e.g contain the title of the
podcast and prefixed by the published date).


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

import dateutil.parser as dateutil_parser
import feedparser
import requests
from sorno import loggingutil
from sorno import webutil
import tzlocal


_LOG = logging.getLogger(__name__)
_PLAIN_LOGGER = None  # will be created in main()


class PodcastDownloader(object):
    def __init__(
        self,
        feed_url,
        out_dir=".",
    ):
        self.feed_url = feed_url
        self.out_dir = out_dir

    def run(self):
        _LOG.info("Find podcasts from %s", self.feed_url)
        parsed = feedparser.parse(self.feed_url)
        entries = parsed['entries']

        num_entries = len(entries)
        for i, entry in enumerate(entries):
            published = entry['published']
            link = entry['link']
            title = entry['title']

            _LOG.info(
                "(%s/%s) Download podcast %s from %s (published at: %s)",
                i + 1,
                num_entries,
                title,
                link,
                published,
            )

            dt = dateutil_parser.parse(published)
            local_dt = dt.astimezone(tzlocal.get_localzone())
            _, ext = os.path.splitext(link)

            new_filename = "{date} {title}{ext}".format(
                date=local_dt.strftime("%Y_%m_%d"),
                title=re.sub(
                    '  +',
                    ' ',
                    re.sub('[^-_a-zA-Z0-9()]', ' ', title),
                ),
                ext=ext,
            )
            new_filepath = os.path.join(self.out_dir, new_filename)
            tmp_new_filepath = new_filepath + ".tmp"

            _LOG.info(
                "Published date in local time: %s, download to file: [%s]",
                local_dt.strftime("%Y/%m/%d %H:%M:%S"),
                tmp_new_filepath,
            )
            if os.path.exists(new_filepath):
                _LOG.info("[%s] already exists, skipped", new_filepath)
                continue

            webutil.download_file(link, tmp_new_filepath)
            _LOG.info("Rename [%s] to [%s]", tmp_new_filepath, new_filepath)
            os.rename(tmp_new_filepath, new_filepath)


def parse_args(cmd_args):
    description = """
        Download podcasts from a feed with appropriate file names. This tool
        find all podcasts from a feed and download them to a directory
        specified by --out_dir. Each file name is consisted of the date in
        local timezone for the published date of the podcast, and the title of
        the podcast.
    """
    parser = argparse.ArgumentParser(
        description=description,
    )
    parser.add_argument(
        "--debug",
        action="store_true",
    )
    parser.add_argument(
        "--out-dir",
        default=".",
        help="The directory to store the podcasts. Default to \"%(default)s\"",
    )
    parser.add_argument(
        "feed_url",
        help="URL of a feed, should point to an xml file",
    )

    args = parser.parse_args(cmd_args)
    return args


def main():
    global _PLAIN_LOGGER

    args = parse_args(sys.argv[1:])

    loggingutil.setup_logger(_LOG, debug=args.debug)
    _PLAIN_LOGGER = loggingutil.create_plain_logger("PLAIN")

    app = PodcastDownloader(args.feed_url, out_dir=args.out_dir)
    app.run()


if __name__ == '__main__':
    main()
