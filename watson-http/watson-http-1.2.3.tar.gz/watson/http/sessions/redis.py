# -*- coding: utf-8 -*-
import collections
from watson.http.sessions import StorageMixin
from watson.common import imports
from watson.common.contextmanagers import suppress
from watson.http.sessions.serializers import Json
with suppress(ImportError):
    import redis


class Storage(StorageMixin):

    """A redis based storage adapter for session data.
    """
    client = None
    serializer = None
    serializer_class = Json
    encoding = 'utf-8'

    def __init__(self, id=None, timeout=None, autosave=True, config=None):
        super(Storage, self).__init__(id, timeout, autosave)
        settings = {'host': 'localhost', 'port': 6379, 'db': 0}
        if config:
            self._process_config(config)
        self.config = collections.ChainMap(config or {}, settings)
        self.serializer = self.serializer_class()

    def _process_config(self, config):
        if 'serializer_class' in config:
            self.serializer_class = imports.load_definition_from_string(
                config['serializer_class'])
            del config['serializer_class']
        if 'encoding' in config:
            self.encoding = config['encoding']
            del config['encoding']

    def open(self):
        if not Storage.client:
            try:
                Storage.client = redis.StrictRedis(**self.config)
            except:
                raise ImportError('You must have redis installed.')

    def close(self):
        self.open()
        Storage.client.connection_pool.disconnect()
        Storage.client = None
        return True

    def load(self):
        self._data = self._load() or {}

    def _load(self):
        self.open()
        data = Storage.client.get(self.id)
        if data:
            return self.serializer.decode(
                data.decode(self.encoding),
                encoding=self.encoding)
        return None

    def _exists(self):
        return Storage.client.exists(self.id)

    def _save(self, expires):
        self.open()
        data = self.serializer.encode(self._data)
        Storage.client.set(self.id, data, self.timeout)

    def _destroy(self):
        self.open()
        Storage.client.delete(self.id)
