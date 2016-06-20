#!/usr/bin/env python
"""
Tools for manipulating Casu logs.
"""

import csv

import argparse

def split(logname):
    """
    Splits the aggregated Casu log file into
    device-specific log files.
    """
    name_base = logname.split('.')[0] + '-'
    devices = dict()
    with open(logname,'rb') as logfile:
        logreader = csv.reader(logfile, delimiter = ';')
        for row in logreader:
            dev = row[0]
            if not dev in devices:
                devices[dev] = dict()
                devices[dev]['file'] = open(name_base + dev + '.csv', 'wb')
                devices[dev]['writer'] = csv.writer(devices[dev]['file'], delimiter = ';')
            devices[dev]['writer'].writerow(row[1:])
    
    # Close all files
    for dev in devices:
        devices[dev]['file'].close()
                

# TODO: Add join function to join several logs in a smart way

# TODO: Add cleanup function to clean up unnecessary split files

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Process raw Casu logs.')
    parser.add_argument('files', metavar = 'filename', nargs='+',
                        help = 'Names of log files to process')

    args = parser.parse_args()
    for logfile in args.files:
        split(logfile)

