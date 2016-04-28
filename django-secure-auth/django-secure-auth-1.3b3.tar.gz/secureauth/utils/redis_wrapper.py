# -*- encoding: utf-8 -*-

from redis import Redis
from secureauth import defaults


class RedisClient(Redis):
    def __init__(self):
        super(RedisClient, self).__init__(
            host=defaults.REDIS_HOST,
            port=defaults.REDIS_PORT,
            db=defaults.REDIS_DB,
            password=defaults.REDIS_PASSWORD)
