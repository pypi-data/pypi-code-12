from ubackup.bucket.base import Bucket
from ubackup import utils
from datetime import datetime
from dateutil import tz

import os
import re

import logging
logger = logging.getLogger(__name__)


class LocalBucket(Bucket):
    TYPE = 'local'
    PATTERN = r'(\.(\d)+)?$'
    FILES_LIMIT = 5

    def __init__(self, path=None, files_limit=None):
        self.local_path = path or self.conf['path']
        self.FILES_LIMIT = files_limit or self.conf.get('limit') or self.FILES_LIMIT

    def log(self, filename, message, level='debug'):
        getattr(logger, level)('%(type)s(%(filename)s): %(message)s' % {
            'type': self.TYPE,
            'filename': filename,
            'message': message
        })

    def abs(self, filename):
        return os.path.join(self.local_path, filename)

    def rotate_file(self, filename):
        files = os.listdir(self.local_path)
        for path in sorted(files, reverse=True):
            if path.startswith(filename):
                cursor = int(re.search(self.PATTERN, path).group(2) or 0)

                if cursor + 1 >= self.FILES_LIMIT:
                    os.remove(self.abs(path))
                else:
                    rotated_file = re.sub(self.PATTERN, '.%s' % (cursor + 1), path)
                    os.rename(
                        self.abs(path),
                        self.abs(rotated_file))

    def push(self, stream, filename, versioning=False):
        self.log(filename, 'start')
        start = datetime.now()

        if versioning:
            self.rotate_file(filename)

        filepath = self.abs(filename)
        with open(filepath, 'w') as fp:
            chunk = stream.read(1024)
            while chunk:
                fp.write(chunk)
                chunk = stream.read(1024)

        self.log(
            filename,
            'pushed in %ss' % utils.total_seconds(datetime.now() - start),
            level='info')

    def pull(self, filename, rev=None):
        # The rev is the versioned filename
        if rev is not None:
            filename = rev

        return open(self.abs(filename), 'r')

    def exists(self, filename):
        return os.path.exists(self.abs(filename))

    def get_revisions(self, filename):

        def revision(filename):
            filepath = self.abs(filename)
            return {
                'id': filename,
                'size': os.path.getsize(filepath),
                'date': datetime.fromtimestamp(os.path.getmtime(filepath), tz=tz.tzlocal())
            }

        revisions = []

        files = os.listdir(self.local_path)
        for path in sorted(files):
            if path.startswith(filename):
                revisions.append(revision(path))

        return revisions
