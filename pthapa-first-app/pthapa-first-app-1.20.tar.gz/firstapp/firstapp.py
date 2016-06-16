"""
provides entry point to main
"""
__version__='0.20'

import sys
from .helpers import Help


def main():
    print('executin firstapp version : ',__version__)
    print('list of arguments : ',sys.argv[1:])

class Foo:
    pass