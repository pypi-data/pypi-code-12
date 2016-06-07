# -*- coding: utf-8 -*-

import redis

import gaia.config as cfg

config = cfg.load_config('app.yaml') or cfg.load_config('redis.yaml') or cfg.load_config('redis.json') or cfg.load_config('redis.cfg')

client = redis.Redis(**config['redis'])
