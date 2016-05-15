#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2013,2014,2016 Jérémie DECOCK (http://www.jdhp.org)

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
TODO...
"""

__all__ = ['transilien']

import argparse
import feedparser

LINES = ['A', 'B', 'C', 'D', 'E', 'H', 'J', 'K', 'L', 'N', 'P', 'R', 'U']

def transilien(line):
    rss_str = None

    line = line.upper()

    if line in LINES:
        rss_url = "http://www.transilien.com/flux/rss/traficLigne?codeLigne=" + line
        feed_dict = feedparser.parse(rss_url)
        entries_set = {entry['title'] for entry in feed_dict.entries}

        rss_str = " ; ".join(entries_set)

    return rss_str


def main():
    parser = argparse.ArgumentParser(description="...")
    parser.add_argument("arg", nargs=1, metavar="STRING",
                        help="The line id (A, B, C, D, E, H, J, K, L, N, P, R, U)")

    args = parser.parse_args()

    print(transilien(args.arg[0]))


if __name__ == '__main__':
    main()
