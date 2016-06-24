# Copyright (c) 2012-2015, Dwight Hubbard.
# Copyrights licensed under the Apache 2.0 License
# See the accompanying LICENSE.txt file for terms.
"""
Confset Debug Mondule

This module contains utility functions useful for troubleshooting confset.

This module can be run from the command line using the following command::

    python -m confset.debug


This will output information like the following::



When run from the command line this will print a dump of information about
the module and it's build information.
"""
from __future__ import print_function
from .__init__ import __version__, __git_version__, __source_url__, \
    __git_hash__, __git_origin__, __git_branch__
import os


def print_debug_info():
    """
    Display information about the redislite build, and redis-server on stdout.
    :return:
    """
    print("confset debug information:")
    print('\tVersion: %s' % __version__)
    print('\tModule Path: %s' % os.path.dirname(__file__))
    print('')
    print('\tSource Code Information')
    if __git_version__:  # pragma: no cover
        print('\t\tGit Source URL: %s' % __source_url__)
        print('\t\tGit Hash: %s' % __git_hash__)
        print('\t\tGit Version: %s' % __git_version__)
        print('\t\tGit Origin: %s' % __git_origin__)
        print('\t\tGit Branch: %s' % __git_branch__)


if __name__ == '__main__':  # pragma: no cover
    print_debug_info()
