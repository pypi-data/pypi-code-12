#!/bin/env python
#-*- encoding=utf8 -*-
#
# Copyright 2013 beager
#
# 作者：zone
#
# 功能：该模块提供缓存相关功能
#
# 版本：V1.0.0
#
import json
import datetime

import redis

"""
缓存模块的封装
"""
class RedisPool:
    """
    RedisPool 的单例化封装
    使用方法:
        from beager_utils import cache
        cache.RedisPool.connect({ 'host':'192.168.1.12', 'port':9979, 'db':2 })

        server = cache.RedisPool.strict_redis()
        
        操作缓存
        server.set('foo', 'bar')
        server.get('foo')

    """
    @classmethod
    def connect(cls, config):
        # host = config['host']
        # port = config['port']
        # db   = config['db']
        cls._pool = redis.ConnectionPool(**config)

    @classmethod
    def strict_redis(cls):
        return redis.StrictRedis(connection_pool = cls._pool)


class Cache(redis.StrictRedis):
    def reconnect(self, redis_config):
        """重新连接缓存服务器
        """
        redis.StrictRedis.__init__(self, **redis_config)

    def __init__(self, config):
        self.reconnect(config)
