from .exceptions import LockError

import redis
import six
import uuid


class LockBase(object):
    """
    """

    # override this with a script
    LUA_ACQUIRE_LOCK = NotImplemented

    # override this with a script
    LUA_RELEASE_LOCK = NotImplemented

    acquire_script = NotImplemented
    release_script = NotImplemented

    def __repr__(self):
        return '<{}: {} - {}>'.format(
            self.__class__.__name__,
            self.name,
            self.uid
        )

    def __init__(self, host_info, name, ttl):
        """
            ttl:
            name:
            host_info:
        """
        self.host_info = host_info
        self.uid = uuid.uuid4().hex
        if not isinstance(name, six.string_types):
            raise ValueError(
                'name must be a string that uniquely identifies the resource '
                'intended to be locked.'
            )
        self.name = name[:]

        if not isinstance(ttl, (int, float)):
            raise ValueError(
                'ttl must be an integer or a float. It inidicates how long the'
                ' lock has to live. (unit milliseconds)'
            )
        # floats will be rounded
        self.ttl = int(ttl)

        self.setup()
        self._checks()

    def _checks(self):
        if not isinstance(self.acquire_script, redis.client.Script):
            raise NotImplementedError(
                'setup must register a redis lua script to self.acquire_script'
            )

        if not isinstance(self.release_script, redis.client.Script):
            raise NotImplementedError(
                'setup must register a redis lua script to self.release_script'
            )

    def setup(self):
        raise NotImplementedError(
            '{}.setup must be overriden'.format(self.__class__.__name__)
        )

    def run_script(self, script, keys, args):
        raise NotImplementedError(
            '{}.runscript must be overriden'.format(self.__class__.__name__)
        )

    def setup_client(self, host_info):
        if isinstance(host_info, dict):
            client = redis.StrictRedis(**host_info)
        else:
            raise ValueError(
                'host_info must be a dictionary of redis connection '
                'options.'
            )
        return client

    def acquire(self):
        return self.run_script(
            self.acquire_script, keys=[self.name, ], args=[self.uid, self.ttl]
        )

    def release(self):
        return self.run_script(
            self.release_script, keys=[self.name, ], args=[self.uid, ]
        )

    def __enter__(self):
        success = self.acquire()
        if not success:
            raise LockError("Could not acquire lock.")
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type is not None:
            pass  # exception caught in the with block
        self.release()
