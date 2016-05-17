# -*- coding: utf-8 -*-

from pymongo import MongoClient

import gaia.config as cfg

config = cfg.load_config('app.yaml') or cfg.load_config('mongo.yaml') or cfg.load_config('mongo.json') or cfg.load_config('mongo.cfg')

client = MongoClient(**config['mongo'])
