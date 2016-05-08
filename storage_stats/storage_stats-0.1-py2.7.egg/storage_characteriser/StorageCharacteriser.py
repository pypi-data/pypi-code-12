#!/usr/bin/python

""" Program for capturing statistics about file sizes in a specified directory.
    Captures minimum, maximum, mean and standard deviation of file sizes.
"""
__author__ = 'Peter May'

import csv
import locale
import math
import os
import progressbar


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
    def __init__(self):
        """ Initialises the Characteriser object
        """
        self.filestats = {}

    def process_directory(self, path, recursive):
        """ Processes the specified directory, extracting file sizes for each file and
            adding to a file extension indexed dictionary.
        :param path: the path to analyse
        :param recursive: true if processing should include sub-directories
        :return:
        """
        bar = progressbar.ProgressBar(max_value=progressbar.UnknownLength)

        # grab file extension and file sizes across all files in the specified directory
        for root, dirs, files in os.walk(path):
            # if only processing the top level, remove dirs so os.walk doesn't progress further
            if not recursive:
                del dirs[:]

            for name in files:
                filename = os.path.join(root, name)
                fname, fext = os.path.splitext(filename)

                if os.path.exists(filename):
                    if fext not in self.filestats:
                        self.filestats[fext] = RunningStat()
                    self.filestats[fext].add(os.stat(filename).st_size)
                bar.update()

    def clear_stats(self):
        """ Clears the file statistics directory
        """
        self.filestats = {}

    def print_stats(self):
        """ Prints the specified statistics to the console in a tabular form
        :return:
        """
        print 'Ext'.ljust(5), \
              '# values'.rjust(12), \
              ' Min Size (bytes)'.rjust(18), \
              'Mean Size (bytes)'.rjust(18), \
              'S.D.'.rjust(12), \
              ' Max Size (bytes)'.rjust(18)

        for ext in self.filestats.keys():

            print ext.ljust(5),
            print locale.format('%12.0f', self.filestats[ext].numbervalues()),
            print locale.format('%18.0f', self.filestats[ext].getmin()),
            print locale.format('%18.0f', self.filestats[ext].getmean()),
            print locale.format('%12.0f', self.filestats[ext].sd()),
            print locale.format('%18.0f', self.filestats[ext].getmax())

    def write_csv(self, csv_file):
        """ Writes the file size statistics to the specified CSV file
        :param csv_file: path of the CSV file to create
        :return:
        """
        with open(csv_file, 'wb') as csvfile:
            statswriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            header = ['Ext', '# Values', 'Min Size (bytes)', 'Mean Size (bytes)', 'S.D.', 'Max Size (bytes)']
            statswriter.writerow(header)

            for ext in self.filestats.keys():
                stats = self.filestats[ext]
                row = [ext, stats.numberValues(), stats.getMin(), stats.getMean(), stats.sd(), stats.getMax()]
                statswriter.writerow(row)
