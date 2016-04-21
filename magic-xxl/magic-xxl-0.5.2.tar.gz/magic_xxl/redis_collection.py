"""
Extends Redis with DataStructure
"""

from redis import Redis
import redis_collections

class RedisCollection(Redis):

    def List(self, key):
        return redis_collections.List(key=key, redis=self)

    def Dict(self, key):
        return redis_collections.Dict(key=key, redis=self)

    def Set(self, key):
        return redis_collections.Set(key=key, redis=self)