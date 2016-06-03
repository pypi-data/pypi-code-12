#!/usr/bin/env python

from __future__ import print_function
from __future__ import absolute_import

import argparse
import sys
import os.path
import runpy

import cython
import pyorcy


def create_parser():
    """ Create and return the parser. """
    parser = argparse.ArgumentParser(
            description='command line utility for the pyorcy package')

    # print version of pyorcy and cython itself
    version_str = ("pyorcy: {} cython: {}".format(
        pyorcy.__version__, cython.__version__))
    parser.add_argument('-V', '--version', action='version',
                        version=version_str)
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        default=False,
                        help='be verbose about actions')
    mode_group = parser.add_mutually_exclusive_group(required=False)
    mode_group.add_argument('-p', '--python',
                            action='store_true',
                            default=False,
                            help='use Python for evaluating function')
    mode_group.add_argument('-c', '--cython',
                            action='store_true',
                            default=True,
                            help='use Cython for evaluating function')
    parser.add_argument('MODULE', nargs=1)
    parser.add_argument('mod_args', nargs=argparse.REMAINDER)
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    # Arguments that drive the behaviour of pyorcy
    pyorcy.USE_CYTHON = True
    if args.python:
        pyorcy.USE_CYTHON = False
    if args.verbose:
        pyorcy.VERBOSE = True

    # Add the location of the module to the sys.path
    module = args.MODULE[0]
    sys.path.append(os.path.dirname(module))

    # Add remaining parameters in globals
    init_globals = {'__args__': args.mod_args}

    # Execute the module
    runpy.run_path(module, init_globals=init_globals, run_name="__main__")


if __name__ == "__main__":
    main()
