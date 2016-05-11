#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''URLer
Usage:
    urler (<host> <port> <path> | <file>)
    urler (-h | --help | --version)

Examples:
    urler example.com 8080 index.html
    urler targets.csv

Assumptions:
    you know what you are doing

Commands:
    host         target host
    port         destination port
    path         URL path
    file         system path to a csv file with the following fields: host,port,path

Options:
    -h, --help    show this help message and exit
    --version     prints program version and exit
'''

from urllib3 import Timeout
from docopt import docopt
import urllib3
import sys


def load_csv_file(csv_file):
    ''' loads csv '''
    try:
        with open(csv_file, 'r') as f:
            return f.readlines()
    except Exception as e:
        sys.exit('urler: fatal - {0}'.format(e))


def create_target(csv_line):
    ''' converts a csv line to a url '''
    try:
        target = csv_line.split(',')
        return (target[0] + ':' + target[1] + "/" + target[2]).rstrip()
    except Exception as e:
        sys.exit('urler: fatal - {0}'.format(e))


def get_csv_url(list):
    ''' HTTP GET multiple urls '''
    try:
        return [(create_target(line), get_url(create_target(line))) for line in list]
    except Exception as e:
        sys.exit('urler: fatal - {0}'.format(e))


def get_url(url):
    ''' HTTP GET a single url '''
    try:
        http = urllib3.PoolManager()
        return (http.request('GET', url, timeout=Timeout(connect=1.0, read=1.0))).data
    except Exception as e:
        # don't stop when a single target fails
        print 'urler: fail - {0}'.format(e)
        return '<error>'


def main():
    ''' main entry point for the script '''
    arguments = docopt(__doc__, version='urler 0.1.0')
    host = arguments['<host>']
    port = arguments['<port>']
    path = arguments['<path>']
    filepath = arguments['<file>']

    if filepath:
        list = load_csv_file(filepath)
        print "\n".join((item[0] + ":\t" + item[1]) for item in get_csv_url(list))
    else:
        url = '{0}:{1}/{2}'.format(host, port, path)
        print get_url(url)

if __name__ == '__main__':
    sys.exit(main())
