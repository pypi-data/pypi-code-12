from __future__ import absolute_import

from .dropbox import DropboxBucket
from .local import LocalBucket


BUCKETS = {
    'dropbox': DropboxBucket,
    'local': LocalBucket
}
