from ubackup.utils import md5_stream, gzip_stream, crypt_stream, unzip_stream, decrypt_stream
from ubackup import settings

import logging
logger = logging.getLogger(__name__)


class Backup(object):

    @property
    def TYPE(self):
        raise NotImplementedError

    @property
    def data(self):
        raise NotImplementedError

    @property
    def unique_name(self):
        raise NotImplementedError

    @property
    def stream(self):
        raise NotImplementedError

    @property
    def crypt_enabled(self):
        return hasattr(settings, 'CRYPT_KEY')

    # -----

    def restore_command(self, stream):
        raise NotImplementedError

    def checksum(self):
        logger.debug('Checksum: %(type)s(%(data)s)' % {
            'type': self.TYPE,
            'data': self.data
        })
        return md5_stream(self.stream)

    def create(self, crypt=True):
        logger.debug('Create: %(type)s(%(data)s)' % {
            'type': self.TYPE,
            'data': self.data
        })

        stream = gzip_stream(self.stream)
        if crypt:
            stream = crypt_stream(stream, settings.CRYPT_KEY)

        return stream

    def restore(self, stream, crypt=True):
        if crypt:
            stream = decrypt_stream(stream, settings.CRYPT_KEY)
        stream = unzip_stream(stream)
        self.restore_command(stream)
