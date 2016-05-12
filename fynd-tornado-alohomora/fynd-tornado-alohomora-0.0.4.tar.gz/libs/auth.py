from tornado.options import options
import redis

from helpers.misc_hepler import get_bool_value


class Authenticate():
    def __init__(self):
        self.auth_enabled = True
        self.redis_port = 6379
        self.redis_db = 0
        self.redis_host = '192.168.1.108'
        self.session_id = 'sessionid_alohomora'
        self.session_prefix = 'session:'
        self.store_auth_required_key = 'store_auth_required'

        if hasattr(options, 'ALOHOMORA_REDIS_HOST'):
            self.redis_host = options.ALOHOMORA_REDIS_HOST
        if hasattr(options, 'IS_AUTH_ENABLED'):
            self.auth_enabled = options.IS_AUTH_ENABLED
        if hasattr(options, 'ALOHOMORA_REDIS_PORT'):
            self.redis_port = options.ALOHOMORA_REDIS_PORT
        if hasattr(options, 'ALOHOMORA_REDIS_DB'):
            self.redis_db = options.ALOHOMORA_REDIS_DB

        self._alohomora_redis = self.get_alohomora_redis()

    @classmethod
    def get_alohomora_redis(self):
        return redis.StrictRedis(host=self.redis_host, port=self.redis_port, db=self.redis_db)