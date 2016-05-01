# -*- coding: utf-8 -*-
# ATENCAO: nao chame este arquivo de redis. Vai entrar em conflito com o modulo redis do sistema

import redis
import os

class RedisConnect(object):

    def __init__(self, host=None, port=None, db=None):

        if host is None:
            host = os.environ.get('REDIS_HOST')

        if port is None:
            port = os.environ.get('REDIS_PORT')

        if db is None:
            db = os.environ.get('REDIS_DB')

        self.server = self.set_server(host,port,db)

    @classmethod
    def set_server(self, host, port, db):

        key = '{}:{}/{}'.format(host,port,db)

        if hasattr(self,'pools') is False:
            self.pools = {}
            self.servers = {}

        if key not in self.pools:
            self.pools[key] = redis.ConnectionPool(
                    host=host, port=port, db=db,
                    max_connections=10)

            self.servers[key] = redis.StrictRedis(connection_pool=self.pools[key])

        return self.servers[key]

    def get(self, key):
        return self.server.get(key)

    def set(self, key, value):
        return self.server.set(key, value)

    def setex(self, key, ttl, value):
        return self.server.setex(key, ttl, value)

    def getset(self, key, value):
        return self.server.getset(key, value)

    def expire(self, key, value):
        return self.server.expire(key, value)

    def exists(self, key):
        return self.server.exists(key)

    def delete(self, key):
        return self.server.delete(key)

    def lpush(self, key, value):
        return self.server.lpush(key, value)

    def lpop(self, key):
        return self.server.lpop(key)
