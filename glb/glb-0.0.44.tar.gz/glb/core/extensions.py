 # -*- coding: utf-8 -*-
from __future__ import unicode_literals

import redis
#from flask.ext.redis import Redis
from redis.exceptions import WatchError
from glb.settings import Config

from .db import DB

REDIS_URL = Config.REDIS_URL
socket2redis = redis.StrictRedis.from_url(REDIS_URL)
redis = redis.StrictRedis.from_url(REDIS_URL)

#redis = Redis()
db = DB(redis)


def allocated_port():
    """ Balancer frontend port decided by GLB """
    pipe = redis.pipeline()
    try:
        pipe.watch(Config.PORTS_NUMBER_COUNT_KEY)
        v = int(redis.get(Config.PORTS_NUMBER_COUNT_KEY))
        if v > Config.PORT_RANGE[0]:
            pipe.decr(Config.PORTS_NUMBER_COUNT_KEY)
            pipe.execute()
            return v
    except WatchError:
        pass
