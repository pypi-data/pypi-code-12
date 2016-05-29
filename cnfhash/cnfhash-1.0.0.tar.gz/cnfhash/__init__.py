#!/usr/bin/env python3

"""
    cnf-hash
    --------

    A library to hash CNF/DIMACS files.

    (C) Lukas Prokop, 2016, Public Domain
"""

from . import hashing

hash_cnf = hashing.hash_cnf
hash_dimacs = hashing.hash_dimacs

__author__ = 'Lukas Prokop'
__version_info__ = ('1', '0', '0')
__version__ = '.'.join(__version_info__)
__license__ = 'Public Domain'
__docformat__ = 'reStructuredText en'
