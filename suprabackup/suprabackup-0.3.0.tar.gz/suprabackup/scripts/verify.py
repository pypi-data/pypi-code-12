#!/usr/bin/python
"""
Usage: suprabackup_verify.py
Author: Matthieu 'Korrigan' Rosinski <mro@quanta-computing.com>

This program checks all recent backups from database

"""
import os
import sys

from suprabackup import db
from suprabackup.logging import setup_logging
from suprabackup.config import load_config
from suprabackup.server import verify_backups


logger = None
opts = None
config = {}


def main():
    """
    Entry point for backup verify

    """
    import argparse
    global opts

    parser = argparse.ArgumentParser(
        description="This program is a tool to check xtrabackup in database",
        epilog="Copyright Quanta 2014")
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Switch to loglevel DEBUG')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose mode')
    parser.add_argument('-f', '--config',
                        help='Location of the configuration file')
    parser.add_argument('-p', '--path',
                        help='Where to store the backups')
    parser.add_argument('-r', '--remove', action='store_true',
                        help='Remove failed backup files')
    opts = parser.parse_args()
    overrides = {}
    logger = setup_logging('suprabackup-verify', verbose=opts.verbose, debug=opts.debug)
    if opts.path:
        overrides['base_path'] = opts.path
    if opts.config:
        config = load_config(role='verify', overrides=overrides, path=opts.config)
    else:
        config = load_config(role='verify', overrides=overrides)
    logger.debug("Loaded configuration file {}".format(config.file))
    session = db.connect_with_config(config, logger)
    if not session:
        sys.exit(1)
    verify_backups(config, logger, session)
    session.commit()
    session.close()


if __name__ == "__main__":
    main()
