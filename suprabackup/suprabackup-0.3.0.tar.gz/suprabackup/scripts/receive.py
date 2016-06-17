#!/usr/bin/python
"""
Usage: suprabackup_receive.py
Author: Matthieu 'Korrigan' Rosinski <mro@quanta-computing.com>

This script is a wrapper to handle xtrabackup uploads for Percona server backups

"""
import os
import sys
import datetime

from suprabackup import db
from suprabackup.logging import setup_logging
from suprabackup.config import load_config
from suprabackup.server import receive_backup


logger = None

opts = None
config = {}


def main():
    """
    Main function for receive_xtrabackup

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
    parser.add_argument('-p', '--path',
                        help='Where to store the backups')
    opts = parser.parse_args()
    overrides = {}
    logger = setup_logging('suprabackup-receive', verbose=opts.verbose, debug=opts.debug)
    if opts.path:
        overrides['base_path'] = opts.path
    if opts.config:
        config = load_config(role='receive', overrides=overrides, path=opts.config)
    else:
        config = load_config(role='receive', overrides=overrides)
    logger.debug("Loaded configuration file {}".format(config.file))
    ip = get_client_ip()
    session = db.connect_with_config(config, logger)
    if not session:
        sys.exit(1)
    receive_backup(config, logger, session, ip)
    session.commit()
    session.close()


def get_client_ip():
    """
    Returns an Host object from SSH_CLIENT environ variable

    """
    ssh_client = os.getenv('SSH_CLIENT')
    if not ssh_client:
        logger.critical("The client does not appear to be a SSH client")
        sys.exit(1)
    return ssh_client.split()[0]


if __name__ == "__main__":
    main()
