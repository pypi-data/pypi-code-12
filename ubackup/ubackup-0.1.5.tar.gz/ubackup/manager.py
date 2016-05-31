import hashlib
import json
import os
from ubackup import settings

import logging
logger = logging.getLogger(__name__)


class Manager(object):
    DATA_FILE = os.path.join(settings.CURRENT_DIR, "ubackup_data.json")
    CRYPT_FLAG = "crypted"

    class ManagerError(Exception):
        pass

    def __init__(self, bucket):
        self.bucket = bucket

    def build_filename(self, backup, crypt=True):
        m = hashlib.md5()
        m.update(backup.unique_name)
        filename = m.hexdigest()

        # Flag the file as crypted
        if backup.crypt_enabled and crypt:
            filename += "-%s" % self.CRYPT_FLAG

        return "%s.gz" % filename

# -----

    def pull_data(self):
        backup_data = {}
        if os.path.exists(self.DATA_FILE):
            with open(self.DATA_FILE, 'r') as fp:
                data = fp.read()
                try:
                    backup_data = json.loads(data)
                except ValueError:
                    pass
        return backup_data

    def push_data(self):
        with open(self.DATA_FILE, 'w') as fp:
            json.dump(self.data, fp)

    @property
    def data(self):
        # Lazy data pulling
        if not hasattr(self, '_cached_data'):
            self._cached_data = self.pull_data()
        return self._cached_data

# -----

    def push_backup(self, backup):
        checksum = backup.checksum()

        filename = self.build_filename(backup)
        if backup.TYPE not in self.data:
            self.data[backup.TYPE] = {}

        if filename in self.data[backup.TYPE]:
            backup_data = self.data[backup.TYPE][filename]
            if checksum == backup_data['checksum']:
                logger.info('Backup already exists with the same version: %s (%s)' % (filename, backup.TYPE))
                return

        stream = backup.create()
        self.bucket.push(stream, filename, versioning=True)

        self.data[backup.TYPE][filename] = {
            'data': backup.data,
            'checksum': checksum
        }

        self.push_data()

    def restore_backup(self, backup, rev):
        filename = self.build_filename(backup)

        # Check if the file exists
        if not self.bucket.exists(filename):
            raise self.ManagerError('%s(%s): the file does not exist' % (self.bucket.TYPE, filename))

        stream = self.bucket.pull(filename, rev['id'])
        backup.restore(stream)

        logger.info('%s(%s) restored, rev:%s' % (backup.TYPE, backup.data, rev['id']))

    def get_revisions(self, backup):
        filename = self.build_filename(backup)
        return self.bucket.get_revisions(filename)
