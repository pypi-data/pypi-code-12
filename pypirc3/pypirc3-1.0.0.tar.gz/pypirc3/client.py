#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import sys

from pypirc import Pypirc

def main():
    ACTION_CREATE = 'create'
    ACTION_SHOW = 'show'

    parser = argparse.ArgumentParser(description = 'command line tool to show or create .pypirc with python3.')
    parser.add_argument('action', choices=[ACTION_CREATE, ACTION_SHOW],
                        help = "define executing action.")
    parser.add_argument('-u', '--username', type = str,
                        help = 'username registed for PyPI account')
    parser.add_argument('-p', '--password', type = str,
                        help = 'password registed for PyPI account')

    options = parser.parse_args()
    action = options.action
    username = options.username
    password = options.password

    pypirc = Pypirc()

    if action == ACTION_CREATE:
        if not (username and password):
            raise Exception(parser.format_usage(), 'username and password are required!')

        pypirc.create(username, password)
        print('Created ~/.pypirc successfully!')
    else:
        if not pypirc.is_exists():
            print("Don't exists ~/.pypirc! See pypirc3 help, and create ~/.pypirc with pypirc3")

        print(pypirc.get_body())

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('{0}error: {1}'.format(e.args[0], e.args[1]))
        sys.exit(1)

    sys.exit(0)
