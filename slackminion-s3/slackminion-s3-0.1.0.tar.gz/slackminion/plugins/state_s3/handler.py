import logging

from boto.s3.connection import S3Connection
from boto.s3.key import Key
from datetime import datetime

from slackminion.plugins.state import BaseStateHandler

from . import version
try:
    from . import commit
except ImportError:
    commit = 'HEAD'


class S3StateHandler(BaseStateHandler):
    def on_load(self):
        logging.getLogger('boto').setLevel(logging.WARN)
        super(S3StateHandler, self).on_load()

    def load_state(self):
        bucket = self._get_s3()
        try:
            key = [k for k in bucket.list(prefix=self.config['prefix'])][-1]
            self.log.debug("Using key %s", key.name)
        except IndexError:
            return '{}'
        state = key.get_contents_as_string()
        return state

    def save_state(self, state):
        bucket = self._get_s3()
        key = Key(
            bucket=bucket,
            name='/'.join([self.config['prefix'], datetime.utcnow().strftime('%Y%m%d%H%M%S')])
        )
        key.set_contents_from_string(state)

    def _get_s3(self):
        if 'aws_access_key' in self.config and 'aws_secret_key' in self.config:
            s3 = S3Connection(self.config['aws_access_key'], self.config['aws_secret_key'])
        else:
            s3 = S3Connection()
        return s3.get_bucket(self.config['bucket'])
