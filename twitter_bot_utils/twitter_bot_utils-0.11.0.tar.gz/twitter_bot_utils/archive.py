# -*- coding: utf-8 -*-
# Copyright 2014 Neil Freeman contact@fakeisthenewreal.org
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from os import path
import json
import csv
from glob import iglob


def read_csv(directory, header=True):
    '''
    Scrape a twitter archive csv, yielding tweet text.

    Args:
        directory (str): CSV file or (directory containing tweets.csv).
        header (boolean): pass False if input CSV has no headers and contains
                          one tweet per line (default: True).

    Returns:
        generator
    '''
    if path.isdir(directory):
        csvfile = path.join(directory, 'tweets.csv')
    else:
        csvfile = directory

    with open(csvfile, 'r') as f:
        if not header:
            fieldnames = ['text']

        for tweet in csv.DictReader(f, fieldnames=fieldnames):
            try:
                tweet['text'] = unicode(tweet['text'], 'utf-8')
            except TypeError:
                pass

            yield tweet


def read_json(directory, data_files='data/js/tweets/*.js'):
    '''
    Scrape a twitter archive file.
    Inspiration from https://github.com/mshea/Parse-Twitter-Archive
    '''
    files = path.join(directory, data_files)

    for fname in iglob(files):
        with open(fname, 'r') as f:
            # Twitter's JSON first line is bogus
            data = f.readlines()[1:]
            data = "".join(data)
            tweetlist = json.loads(data)

        for tweet in tweetlist:
            yield tweet


def read_text(data_file):
    with open(data_file, 'r') as f:
        data = f.readlines()

    for tweet in data:
        try:
            yield unicode(tweet.rstrip(), 'utf-8')
        except TypeError:
            yield tweet.rstrip()
