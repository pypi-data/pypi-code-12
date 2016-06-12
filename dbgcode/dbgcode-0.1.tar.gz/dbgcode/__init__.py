"""
write debug code with confidence
dbgcode is a python package that make it easy
to remove debug code after you finish debugging

example usage:
file: f.py

    x = []
    for i in range(1, 100):
        for j in range(1, 100):
            # dbg
            print("i", i)
            print("j", j)
            # /dbg
            if i % 3 == 0 and j % 3 == 0:
                print("(i, j) ", (i, j))  # _dbg
                x.append((i, j))

    save this file and then in the command line

        $ dbgcode clean f.py

    the result is:
        x = []
        for i in range(1, 100):
            for j in range(1, 100):
                if i % 3 == 0 and j % 3 == 0:
                    x.append((i, j))

:Author: Ali Faki <alifaki077@gmail.com>
:LICENSE: MIT (see LICENSE file for more information)
Copyright 2016 by Ali Faki
"""

__title__ = "dbgcode"
__version__ = "0.0.1"
__license__ = "MIT"
__author__ = "Ali Faki"
__copyright__ = 'Copyright 2016 Ali Faki'

from .api import clean, clean_file
