#!/usr/bin/python

# Copyright 2016 Peter May
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

""" Program for capturing statistics about file sizes in a specified directory.
    Captures minimum, maximum, mean and standard deviation of file sizes.
"""
__author__ = 'Peter May'

import csv
import math
import os
import progressbar
import scandir
from collections import defaultdict


class RunningStat(object):
    """ Object for capturing statistics related to a specific file extension.
        Captures minimum file size, maximum file size, and the running population
        mean and standard deviation.

        Code adapted from wiki page https://en.m.wikipedia.org/wiki/Algorithms_for_calculating_variance
    """
    def __init__(self):
        self.n = 0
        self.m = 0.0
        self.M2 = 0.0

        self.min = 0.0
        self.max = 0.0

    def add(self, x):
        """ Adds the specified file size to the statistics for this file extension.
            Specifically, it keeps running values for the minimum, maximum, mean and
            standard deviation.
        :param x: file size to add
        :return:
        """
        self.n += 1
        delta = x - self.m
        self.m += delta/self.n
        self.M2 += delta*(x-self.m)

        if self.n == 1:
            self.min = x
            self.max = x
        else:
            if x < self.min:
                self.min = x
            if x > self.max:
                self.max = x

    def numbervalues(self):
        """ Returns the number of file sizes added for this file extension
        :return: the number of file size values added
        """
        return self.n

    def getmin(self):
        """ Returns the minimum file size added for this file extension
        :return: the minimum file size
        """
        return self.min

    def getmax(self):
        """ Returns the maximum file size added for this extension
        :return: the maximum file size
        """
        return self.max

    def getmean(self):
        """ Returns the running mean average file size for all sizes added
            when this method is called
        :return: the population mean average file size
        """
        return self.m

    def variance(self):
        """ Returns the running variance in file sizes for all sizes added
            when this method is called
        :return: the variance in file sizes about the mean
        """
        if self.n > 1:
            return self.M2/self.n
        else:
            return 0.0

    def sd(self):
        """ Returns the running standard deviation in file sizes for all sizes
            added when this method is called.
        :return: the standard deviation in file sizes about the mean
        """
        return math.sqrt(self.variance())


class Characteriser(object):
    def __init__(self, mapfile):
        """ Initialises the Characteriser object. In particular, this loads (either the default or user specified)
            file extension mappings. These are lists of similar file extensions that should be counted as the
            same when aggregating results.
        :param mapfile: text file specifying similar file extension mappings
        """
        self.filestats = {}
        self.extmap = self._load_extension_mappings(mapfile)

    def _load_extension_mappings(self, mapfile):
        """ Loads file extension mappings, e.g. .jpeg to jpg
        :param mapfile: text file specifying similar file extension mappings
        :return: a defaultdict of extension mappings
        """
        maps = defaultdict(lambda: None)

        if mapfile is None:
            mapfile = os.path.join(os.path.dirname(__file__), 'data', 'extensionmapping')
        with open(mapfile, 'r') as fmap:
            for line in fmap.readlines():
                linemaps = line.strip().split(",")
                for e in linemaps:
                    maps[e] = linemaps[0]
        return maps

    def _convert_extension(self, ext):
        """ Converts the specified file extension to a known base extension,
            e.g. .jpeg to .jpg
        :param ext: the file extension to convert
        :return: the converted file extension if mapping available, otherwise just the supplied extension
        """
        newext = self.extmap[ext]
        if newext is None:
            newext = ext
        return newext

    def _count_dirs(self, path, recursive=True):
        """ Counts the number of files within the specified directory
        :param path: the top level path to count files in
        :param recursive: true if counting should include sub-directories
        :return: the number of files in the specified path
        """
        count = 0
        try:
            for p in scandir.scandir(path):
                if p.is_file():
                    count += 1
                if recursive and p.is_dir():
                    count += self._count_dirs(p.path, recursive)
        except (IOError, OSError) as e:
            print "Permission Error ({0}): {1} for {2}".format(e.errno, e.strerror, path)

        return count

    def process_directory(self, path, recursive=True, timing=True):
        """ Processes the specified directory, extracting file sizes for each file and
            adding to a file extension indexed dictionary.
        :param path: the path to analyse
        :param recursive: true if processing should include sub-directories
        :param timing: true if path should be preprocessed to provide guidance on run-time
        :return:
        """

        # get number of files - have to scan dir once to start with
        print "\n\rProcessing {0}...".format(path)
        bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength)

        # If user wants more accurate timing, preprocess directory to count files
        if timing:
            numfiles = self._count_dirs(path, recursive)
            bar.start(numfiles)

        # grab file extension and file sizes across all files in the specified directory
        for root, dirs, files in scandir.walk(path, followlinks=False):
            # if only processing the top level, remove dirs so os.walk doesn't progress further
            if not recursive:
                del dirs[:]

            for name in files:
                filename = os.path.join(root, name)
                fname, fext = os.path.splitext(filename)
                fext = self._convert_extension(fext.lower())   # lowercase all filenames

                if os.path.exists(filename):
                    if fext not in self.filestats:
                        self.filestats[fext] = RunningStat()
                    self.filestats[fext].add(os.stat(filename).st_size)
                bar.update(bar.value+1)
        bar.finish()

    def clear_stats(self):
        """ Clears the file statistics directory
        """
        self.filestats = {}

    def print_stats(self):
        """ Prints the specified statistics to the console in a tabular form
        :return:
        """

        # get maximum key length and use to create formatting string
        maxkeylen = len(max(self.filestats, key=len))
        hdrstring = "{:<"+str(maxkeylen)+"} {:>12} {:>18} {:>18} {:>12} {:>18}"
        fmtstring = "{:<"+str(maxkeylen)+"} {:>12d} {:>18.0f} {:>18.0f} {:>12.0f} {:>18.0f}"

        print ""
        print hdrstring.format("Ext", "# values", "Min Size (bytes)", "Mean Size (bytes)", "S.D.", "Max Size (bytes)")

        for ext in sorted(self.filestats.keys()):
            print fmtstring.format(ext,
                                   self.filestats[ext].numbervalues(),
                                   self.filestats[ext].getmin(),
                                   self.filestats[ext].getmean(),
                                   self.filestats[ext].sd(),
                                   self.filestats[ext].getmax())

    def write_csv(self, csv_file, strindex=None):
        """ Writes the file size statistics to the specified CSV file
        :param csv_file: path of the CSV file to create
        :param strindex: if specified, an index number to append to the filename
        :return:
        """
        filename = csv_file
        if strindex is not None:
            filename = csv_file[0:-4]+"-"+str(strindex)+csv_file[-4:]

        with open(filename, 'wb') as csvfile:
            statswriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            header = ['Ext', '# Values', 'Min Size (bytes)', 'Mean Size (bytes)', 'S.D.', 'Max Size (bytes)']
            statswriter.writerow(header)

            for ext in sorted(self.filestats.keys()):
                stats = self.filestats[ext]
                row = [ext, stats.numbervalues(), stats.getmin(), stats.getmean(), stats.sd(), stats.getmax()]
                statswriter.writerow(row)
