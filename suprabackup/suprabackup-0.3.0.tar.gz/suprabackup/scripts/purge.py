#!/usr/bin/python
"""
Usage: suprabackup_purge.py
Author: Matthieu 'Korrigan' Rosinski <mro@quanta-computing.com>

This program purges expired backups from files

"""
import os
import sys

from suprabackup import db
from suprabackup.logging import setup_logging
from suprabackup.config import load_config
from suprabackup.server import purge_backups


logger = None
opts = None
config = None


def main():
    """
    Entry point for suprabackup purge

    """
    import argparse
    global opts
    global logger
    global config

    parser = argparse.ArgumentParser(
        description='This program is a wraper for receiving Xtrabackup uploads and storing them',
        epilog='Copyright Quanta 2014')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Switch to loglevel DEBUG')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose mode')
    parser.add_argument('-f', '--config',
                        help='Location of the configuration file')
    opts = parser.parse_args()
    logger = setup_logging('suprabackup-purge', verbose=opts.verbose, debug=opts.debug)
    if opts.config:
        config = load_config(role='purge', path=opts.config)
    else:
        config = load_config(role='purge')
    logger.debug("Loaded configuration file {}".format(config.file))
    session = db.connect_with_config(config, logger)
    if not session:
        sys.exit(1)
    purge_backups(config, logger, session)
    session.commit()
    session.close()


if __name__ == "__main__":
    main()
