#!/usr/bin/env python

import argparse
import logging

from rabbit_backup.rabbit_dropbox import get_dropbox_access_token, BackupJob

logger = logging.getLogger(__name__)


def setup_log(log_file):
    log_format = "%(asctime)s [%(name)s] [%(levelname)-5.5s]  %(message)s"
    logging.basicConfig(level=logging.INFO,
                        format=log_format,
                        datefmt="%H:%M:%S", filemode='a')

    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.INFO)
    consoleHandler.setFormatter(logging.Formatter(log_format))
    logging.getLogger().addHandler(consoleHandler)

    fileHandler = logging.FileHandler(log_file)
    fileHandler.setFormatter(logging.Formatter(log_format))
    fileHandler.setLevel(logging.INFO)
    logging.getLogger().addHandler(fileHandler)


def main():
    access_token = get_dropbox_access_token()

    parser = argparse.ArgumentParser(description='Passing parameter for rabbit youtube....')

    parser.add_argument('--remote_folder', '-r', help='remote folder')
    parser.add_argument('--retention_days', '-d', help='retention days', type=int)
    parser.add_argument('--log_file', '-l', help='log path')
    parser.add_argument('local_file', help='local file', nargs='+')

    args = parser.parse_args()

    remote_folder = args.remote_folder
    retention_days = int(args.retention_days)
    log_file = args.log_file or '/tmp/rabbit-backup.log'
    local_file = args.local_file

    setup_log(log_file)
    logger.info('backup job summary: backup %s to %s and remove backup files %s days ago' %
                (local_file, remote_folder, retention_days))

    rabbit_dropbox_job = BackupJob(access_token, remote_folder, retention_days)
    rabbit_dropbox_job.backup_and_clear_history_data(local_file)


if __name__ == '__main__':
    main()

