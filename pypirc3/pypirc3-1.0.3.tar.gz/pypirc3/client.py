#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys
from pypirc3.option import *
from pypirc3.pypirc import Pypirc

def main():
    parser = argparse.ArgumentParser(description = 'command line tool to show or create .pypirc with python3.')
    parser.add_argument('action', choices=[ACTION_CREATE, ACTION_SHOW],
                        help = "define executing action.")
    parser.add_argument('-u', '--username', type = str,
                        help = 'username registed for PyPI account')
    parser.add_argument('-p', '--password', type = str,
                        help = 'password registed for PyPI account')

    options = parser.parse_args()

    pypirc = Pypirc(options.action, options.username, options.password)
    result, msg = pypirc.execute()
    print(msg)
    sys.exit(result)


if __name__ == '__main__':
    main()
