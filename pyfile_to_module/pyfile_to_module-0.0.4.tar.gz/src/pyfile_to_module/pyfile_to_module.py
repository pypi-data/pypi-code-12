#!/usr/bin/env python
"""
pyfile_to_module

Simple util to convert a python filename like
some_package/some_module/some_file.py to some_package.some_module.some_file
style module name.

"""

__author__ = 'evansde77@gmail.com'
__version__="0.0.1"

import argparse
import os
import re
import sys


def build_parser():
    """build command line parser and process CLI options"""
    parser = argparse.ArgumentParser(description='CLI util for converting filenames to module names')
    parser.add_argument(
        'filename', metavar='filename', type=str, nargs=1,
        help='filename to convert to modulename'
    )
    parser.add_argument(
        '--prefix', '-p', dest='prefix', default=None, help='dir prefix to strip from the filename'
    )
    parser.add_argument(
        '--walk-pythonpath', '-w',
        default=False,
        action='store_true',
        help='walk python path entries to find matching prefix instead of supplying it',
        dest='walk'
    )
    args = parser.parse_args()
    return args


end_replace = lambda p, sub, s: re.sub('{0}$'.format(p), sub, s)
start_replace = lambda p, sub, s: re.sub('^{0}'.format(p), sub, s)


def find_prefix(filename):
    """
    walk through pythonpath and use it to find the appropriate module prefix
    string for the filename

    """
    filename = os.path.abspath(filename)
    # find all entries in the path that filename starts with
    matches = (x for x in sys.path if filename.startswith(x))
    # pick the deepest path
    best_match = max(matches)
    return best_match


def convert_name(filename, prefix=None):
    """
    convert_name

    Given filename:
     if prefix is provided, remove prefix from start of string
     remove .py from end of string
     swap / for .
     return the output

    """
    full_filename = os.path.abspath(filename)
    if prefix:
        full_filename = start_replace(prefix, '', full_filename)
    if full_filename.startswith('/'):
        full_filename = start_replace('/', '', full_filename)
    full_filename = end_replace('.py', '', full_filename)
    full_filename = full_filename.replace('/', '.')
    return full_filename


def main():
    """
    main entry point for CLI
    """
    args = build_parser()
    filename = args.filename[0]
    prefix = args.prefix
    if args.walk:
        prefix = find_prefix(filename)
    result = convert_name(filename, prefix)
    sys.stdout.write(result)
    sys.stdout.write('\n')
    sys.exit(0)


if __name__ == '__main__':
    main()
