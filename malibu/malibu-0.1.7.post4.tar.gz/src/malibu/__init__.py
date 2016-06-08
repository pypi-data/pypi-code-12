# -*- coding: utf-8 -*-
from malibu import command
from malibu import config
from malibu import database
from malibu import design
from malibu import text
from malibu import util

import subprocess

__git_label__ = ''
try:
    __git_label__ = subprocess.check_output(
        [
            'git',
            'rev-parse',
            '--short',
            'HEAD'
        ])
except subprocess.CalledProcessError:
    __git_label__ = 'RELEASE'

__version__ = '0.1.7-4'
__release__ = '{}-{}'.format(__version__, __git_label__).strip()
__doc__ = """
malibu is a collection of classes and utilities that make writing code
a little bit easier and a little less tedious.

The whole point of this library is to have a small codebase that could
be easily reused across projects with nice, easily loadable chunks that
can be used disjointly.
"""
