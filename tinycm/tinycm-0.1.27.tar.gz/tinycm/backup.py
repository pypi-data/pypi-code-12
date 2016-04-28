import os
import shutil
import logging

current_id = None


def backup_file(path):
    logger = logging.getLogger('tinycm')
    if not current_id:
        raise Exception('Backup requested before unique id is generated')
    logger.debug('Starting backup for {}'.format(path))
    backup_dir = '/var/backups/tinycm'
    backupfile = os.path.join(backup_dir, current_id, path)
    backupfile_path = os.path.dirname(backupfile)
    os.makedirs(backupfile_path, 0o700, exist_ok=True)
    logger.debug('Backup to: {}'.format(backupfile))
    shutil.copy2(path, backupfile)
