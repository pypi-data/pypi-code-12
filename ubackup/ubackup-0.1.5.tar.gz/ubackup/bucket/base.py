from ubackup import settings
from requests import Response

import logging
logger = logging.getLogger(__name__)


class Bucket(object):
    def __init__(self):
        pass

    class BucketError(Exception):
        def __init__(self, message, data={}):
            if isinstance(data, Response):
                try:
                    data = data.json()
                except:
                    data = data.text
            super(Bucket.BucketError, self).__init__(message, data)

    @property
    def conf(self):
        return settings.BUCKETS[self.TYPE]

    @property
    def TYPE(self):
        raise NotImplementedError

    def push(self, stream, name, versioning=False):
        raise NotImplementedError

    def pull(self, name):
        raise NotImplementedError

    def exists(self, name):
        raise NotImplementedError
