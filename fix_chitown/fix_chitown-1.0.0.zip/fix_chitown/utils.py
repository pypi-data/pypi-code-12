"""Utilities for chitown fixer."""

import os
import sys
import argparse

db_login_filepath = os.path.join(os.path.dirname(__file__), 'db_details.txt')


def get_db_login(path=db_login_filepath):
    """Get login details for database from file."""
    with open(path, 'r') as f:
        lines = [line.strip() for line in f]
        login_dict = {i.split(":")[0].strip(): i.split(":")[1].strip()
                      for i in lines}
    return login_dict


def process_args(args):
    """Return options dictionary {arg: value}."""
    parser = argparse.ArgumentParser(description="updates the lahman db")

    parser.add_argument('-q',
                        '--path',
                        default=db_login_filepath,
                        help='path to file with db login details')

    parser.add_argument('-l',
                        '--host',
                        default='localhost',
                        help='host of lahman db')

    parser.add_argument('-u',
                        '--username',
                        default='root',
                        help='username for lahman db')

    parser.add_argument('-p',
                        '--password',
                        default='',
                        help='password for lahman db')

    parser.add_argument('-d',
                        '--database',
                        default='lahmandb',
                        help='name of database')
    options = parser.parse_args(args)
    return vars(options)


def flags_to_login_details(args):
    """Return dictionary with db login details from flags."""
    options = process_args(args)
    # print(repr(args))
    # check args is -q and a path OR complete login
    if len(args) == 2 and args[0] in ['-q', '--path']:
        # print("verify path here.")
        path = options['path']
        # print("path = {}").format(path)
    elif len(args) == 0:
        print("path is = default path")
        path = options['path']
        print("path: {}").format(path)
    elif len(args) == 8:
        # print("verify that all the deets are flagged")
        path = None
        # this is ugly. if db and database lined up could use dict_comp
        acceptable_flags = ['-l', '--host',
                            '-u', '--username',
                            '-p', '--password',
                            '-d', '--database']
        for count, elem in enumerate(args):
            if count % 2 == 0:
                # print(repr(elem))
                assert elem in acceptable_flags
            # could run further verification here
            '''
            else:
                print elem
            '''

    elif len(args) != 1 and args[0] not in ['-h', '--help']:
        print("FAILURE: Check your flags.")

    assert path or len(args) == 8

    # print options
    '''
    if options:
        for option in options:
            print("{}: {}").format(option, repr(options[option]))
    '''

    if path:
        try:
            login_dict = get_db_login(options['path'])
        except Exception as e:
            print("Problems accessing path.")
            print e
            sys.exit()
    else:
        login_dict = {'username': options['username'],
                      'host': options['host'],
                      'password': options['password'],
                      'db': options['database']}

    if login_dict['password'] in ["''", '""']:
        login_dict['password'] = ''

    # print login details
    '''
    for key in login_dict:
        print("{}: {}").format(key, login_dict[key])
    '''

    return login_dict
