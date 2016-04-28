import os
import shutil

current_id = None


def backup_file(path):
    if not current_id:
        raise Exception('Backup requested before unique id is generated')
    backup_dir = '/var/backups/tinycm'
    backupfile = os.path.join(backup_dir, current_id, path)
    backupfile_path = os.path.dirname(backupfile)
    os.makedirs(backupfile_path, 0o700, exist_ok=True)
    shutil.copy2(path, backupfile)