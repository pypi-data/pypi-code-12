from collections import namedtuple
import time

import blinker
import boto3
import tinydb


Key = namedtuple('Key', ['name', 'etag', 'size', 'storage_class',
                         'last_modified', 'owner_id', 'owner_display_name'])


class BucketObserver(object):
    # Signals
    key_created = blinker.signal('key_created')
    key_exists = blinker.signal('key_exists')
    key_updated = blinker.signal('key_updated')
    key_deleted = blinker.signal('key_deleted')

    def __init__(self, bucket_name, access_key_id, secret_access_key,
                 db_file_path, region_name='us-east-1'):
        self.bucket_name = bucket_name
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.db = tinydb.TinyDB(db_file_path)
        self.region_name = region_name

    def __del__(self):
        self.db.close()

    def __repr__(self):
        return "<BucketObserver object observing '%s'>" % self.bucket_name

    def __call__(self, *args, **kwargs):
        return self.observe(*args, **kwargs)

    def _get_s3client(self):
        return boto3.client(
            's3',
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            region_name=self.region_name
        )

    def _key_iterator(self):
        client = self._get_s3client()

        for obj in client.list_objects(Bucket=self.bucket_name)['Contents']:
            yield Key(
                name=obj['Key'],
                etag=obj['ETag'],
                size=obj['Size'],
                storage_class=obj['StorageClass'],
                last_modified=obj['LastModified'].timestamp(),
                owner_id=obj['Owner']['ID'],
                owner_display_name=obj['Owner']['DisplayName']
            )

    def _fetch_live_keys(self):
        keys = list(key for key in self._key_iterator())

        query = tinydb.Query()
        data = {'bucket': self.bucket_name, 'keys': keys, 'time': time.time()}
        self.db.update(data, query.bucket == self.bucket_name) or \
            self.db.insert(data)

        return keys

    def _fetch_cached_keys(self):
        query = tinydb.Query()
        data = self.db.get(query.bucket == self.bucket_name)
        keys = [Key(*l) for l in data['keys']] if data is not None else []
        return keys

    def observe(self):
        # Update live and from cache
        cached = set(self._fetch_cached_keys())
        live = set(self._fetch_live_keys())

        # Set theory
        created = set()
        exists = live.intersection(cached)
        updated = set()
        deleted = set()

        cached_names = [key.name for key in cached]

        for key in live.difference(cached):
            updated.add(key) if key.name in cached_names else created.add(key)

        updated_names = [key.name for key in updated]

        for key in cached.difference(live):
            if key.name in cached_names and key.name not in updated_names:
                deleted.add(key)

        # Send signals
        [self.key_created.send(self, key=key) for key in created]
        [self.key_exists.send(self, key=key) for key in exists]
        [self.key_updated.send(self, key=key) for key in updated]
        [self.key_deleted.send(self, key=key) for key in deleted]

        # Return every set in a dict
        return dict(created=created, exists=exists, updated=updated,
                    deleted=deleted)
