import json

try:
    from pymemcache.client.base import Client
    from pymemcache.client.hash import HashClient
except ImportError as e:
    raise ImportError('Failed to import "pymemcache" ({})'.format(e))

from .abstract import Abstract
from .abstract import NotSupported

def get_default_client(server_config = None):
    if server_config and isinstance(server_config, list):
        return HashClient(
            server_config,
            serializer   = serializer,
            deserializer = deserializer
        )

    return Client(
        server_config or ('127.0.0.1', 11211),
        serializer   = serializer,
        deserializer = deserializer
    )

def serializer(key, value):
    if type(value) == str:
        return value, 1

    return json.dumps(value), 2

def deserializer(key, value, flags):
    actual_value = value.decode('utf-8')

    if flags == 1:
        return actual_value

    if flags == 2:
        return json.loads(actual_value)

    # If all else fail, the deserializer will forcefully decode the object.
    try:
        return json.loads(actual_value)
    except Exception as e:
        return actual_value

class Memcached(Abstract):
    """ Adapter for Memcached """
    def __init__(self, storage = None, namespace = None, delimiter = ':'):
        self._storage   = storage
        self._namespace = namespace or ''
        self._delimiter = delimiter

    def get(self, key):
        actual_key = self._actual_key(key)

        return self._storage.get(actual_key)

    def set(self, key, value, ttl = None):
        actual_key = self._actual_key(key)

        self._storage.set(actual_key, value)

    def remove(self, key):
        actual_key = self._actual_key(key)

        self._storage.delete(actual_key)

    def find(self, *args, **kwargs):
        raise NotSupported()

    def _actual_key(self, key):
        if not self._namespace:
            return key

        return '{}{}{}'.format(self._namespace, self._delimiter, key)
