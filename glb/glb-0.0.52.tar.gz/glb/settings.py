# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from os import environ


class EnvConfigType(type):

    def __getattribute__(cls, key):
        value = object.__getattribute__(cls, key)
        env = environ.get(key)
        if env is not None:
            value = type(value)(env)
        return value


class Config(object):

    __metaclass__ = EnvConfigType

    DEBUG = environ.get('DEBUG', True),
    REDIS_URL = 'redis://%s:%s/%s' % (
        environ.get('REDIS_HOST', 'localhost'),
        environ.get('REDIS_PORT', '6379'),
        environ.get('REDIS_DB', '2'),
    )
    PORT_RANGE = (50000, 61000)
    PORTS_NUMBER_COUNT_KEY = 'glb:ports_number_count'
    LATEST_VERSION = 'glb:balancer_latest_version'
    LISTEN_REDIS_CHANNEL = 'glb:data_last_update_time'
    GLB_URL = environ.get('GLB_URL', 'glb.guokr.com')
