#!/usr/bin/python
"""Scrapes the 1000 pegs from http://www.rememberg.com/Peg-list-1000/


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
import random
import re
import sys
import time

import requests

from sorno import loggingutil


_LOG = logging.getLogger(__name__)
_PLAIN_LOGGER = None  # will be created in main()


class App(object):
    MAIN_PAGE_URL = "http://www.rememberg.com/Peg-list-1000/"

    def run(self):
        # a list of 2-tuple. Each 2-tuple is (number, word)
        pegs = []

        # scrape the pegs from the initial page
        _LOG.info("Fetch from %s", self.MAIN_PAGE_URL)
        page = requests.get(self.MAIN_PAGE_URL).text
        pegs.extend(
            self.scrape_pegs(
                page,
                1,
                50,
            )
        )

        while True:
            res = self.get_next_page_url(page)
            if res is None:
                break

            url, start, end = res
            _LOG.info("Fetch from %s", url)
            page = requests.get(url).text
            pegs.extend(self.scrape_pegs(page, start, end))

        for index, word in pegs:
            print("%-3s. %s" % (index, word))

    def scrape_pegs(self, page_html, starting_peg_number, ending_peg_number):
      _LOG.info(
          "Scraping for pegs from %s to %s",
          starting_peg_number,
          ending_peg_number,
      )

      pegs = []

      for line in page_html.split("\n"):
          line = line.strip()
          matched = re.match(r"<big>(\d+)\.</big>.*<strong>(.*)</strong>", line)
          if matched:
              pegs.append(matched.groups())

      return pegs

    def get_next_page_url(self, page_html):
      """
      Get the url that links to the subsequent page, given the current page html
      in str

      Args:
          str, page_html
      Return:
          If the next page url is found, returns (str, int, int), a 3-tuple of
          url, starting number, and ending number. Otherwise, None.

      """
      for line in page_html.split("\n"):
          line = line.strip()
          # shortcut for matching before checking the regex
          if line.startswith('<a href="/Peg-list-1000/'):
              matched = re.match('<a href="(.*?)"><strong>Next:', line)
              if matched:
                  next_url = matched.groups()[0]
                  _LOG.debug("Next url is found: %s", next_url)
                  next_url = "http://www.rememberg.com" + next_url
                  start_and_end_matched = re.match(
                      r".*/peg-(\d+)-to-(\d+)",
                      next_url,
                  )
                  if start_and_end_matched:
                      start, end = start_and_end_matched.groups()
                      return next_url, start, end
                  else:
                      _LOG.warn("Start and end not found in line: %s", line)
              elif "Next" in line:
                  _LOG.warn("Unexpected missing url in line: %s", line)

      return None


def parse_args(cmd_args):
    description = """
A script to scrape the 1000 pegs from http://www.rememberg.com/Peg-list-1000/
    """
    parser = argparse.ArgumentParser(
        description=description,
        # formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--debug",
        action="store_true",
    )

    args = parser.parse_args(cmd_args)
    return args


def main():
    global _PLAIN_LOGGER

    args = parse_args(sys.argv[1:])

    loggingutil.setup_logger(_LOG, debug=args.debug)
    _PLAIN_LOGGER = loggingutil.create_plain_logger("PLAIN")

    app = App()
    app.run()


if __name__ == '__main__':
    main()
