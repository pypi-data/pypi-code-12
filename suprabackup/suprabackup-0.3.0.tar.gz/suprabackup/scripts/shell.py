#!/usr/bin/python
"""
Usage: suprashell.py
Author: Matthieu 'Korrigan' Rosinski <mro@quanta-computing.com>

This script gives a shell to Suprabackup database using the ORM

"""
import os
import sys


from suprabackup import db
from suprabackup.config import load_config
from suprabackup.logging import setup_logging
from suprabackup.cli import cli, shell


opts = None
config = None
logger = None


def main():
    """
    Entrypoint for suprash

    """
    import argparse
    global opts
    global config

    parser = argparse.ArgumentParser(
        description="This program is a tool to interact with suprabackup database",
        epilog="Copyright Quanta 2014")
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Switch to loglevel DEBUG')
    parser.add_argument('-f', '--config',
                        help='Location of the configuration file')
    parser.add_argument('command', nargs='?',
                        help='The command to execute. If not specified, a shell will be given.')
    parser.add_argument('args', nargs='*',
                        help='The command arguments')
    opts = parser.parse_args()
    logger = setup_logging('suprashell', verbose=True, debug=opts.debug, no_syslog=True)
    if opts.config:
        config = load_config(role='shell', path=opts.config)
    else:
        config = load_config(role='shell')
    logger.debug("Loaded config from {}".format(config.file))
    session = db.connect_with_config(config, logger)
    if opts.command:
        cli(session, logger, opts.command, *opts.args)
    else:
        shell(session, config)
    session.commit()
    session.close()


if __name__ == "__main__":
    main()
