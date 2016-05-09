# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
import json
from glb.settings import Config


def json_loads(val):
    try:
        return json.loads(val)
    except ValueError:
        return val


class DB(object):

    def __init__(self, redis):
        self.redis = redis
        if not self.redis.exists(Config.PORTS_NUMBER_COUNT_KEY):
            self.redis.set(Config.PORTS_NUMBER_COUNT_KEY, Config.PORT_RANGE[1])

    def update_service_latest_version(self):
        latest_version = "%s_%s" % ('balancer', str(datetime.datetime.now()))
        self.redis.publish(Config.LISTEN_REDIS_CHANNEL,  latest_version)
        self.redis.set(Config.LATEST_VERSION, latest_version)

    def save(self, prefix_key, primary_key, data):
        if not data or primary_key not in data.keys():
            return False
        obj_id = data[primary_key]
        if not self.redis.sismember(prefix_key, obj_id):
            self.redis.sadd(prefix_key, obj_id)
            base_key = '%s:%s' % (prefix_key, obj_id)
            data.pop(primary_key)
            if data:
                for k, v in data.iteritems():
                    data[k] = json.dumps(v)
                self.redis.hmset(base_key, data)
            self.update_service_latest_version()
            return True
        return False

    def fetch_one(self, prefix_key, primary_key, obj_id):
        if self.redis.sismember(prefix_key, obj_id):
            base_key = '%s:%s' % (prefix_key, obj_id)
            mapping = self.redis.hgetall(base_key)
            for k, v in mapping.iteritems():
                mapping[k] = json_loads(v)
            mapping[primary_key] = obj_id
            return mapping

    def fetch_all(self, prefix_key, primary_key):
        obj_ids = self.redis.smembers(prefix_key)
        rs = [self.fetch_one(prefix_key, primary_key, obj_id)
              for obj_id in obj_ids]
        return rs

    def fetch_all_obj_ids(self, prefix_key, primary_key):
        return self.redis.smembers(prefix_key)

    def delete_one(self, prefix_key, obj_id):
        if self.redis.sismember(prefix_key, obj_id):
            base_key = '%s:%s' % (prefix_key, obj_id)
            self.redis.delete(base_key)
            self.redis.srem(prefix_key, obj_id)
            self.update_service_latest_version()
            return True
        return False

    def update(self, prefix_key, obj_id, vals):
        if self.redis.sismember(prefix_key, obj_id):
            base_key = '%s:%s' % (prefix_key, obj_id)
            for k, v in vals.iteritems():
                vals[k] = json.dumps(v)
            self.redis.hmset(base_key, vals)
            self.update_service_latest_version()
            return True
        return False
