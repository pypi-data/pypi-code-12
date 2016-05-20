# -*- coding:utf-8 -*-

import socket
import unittest
import config
import redis
import json

from .anti import getServer, MAX_OPEN_LINKS, openYandex


class AntiTest(unittest.TestCase):
    def setUp(self):
        self.rds = redis.Redis(**config.ANTI_REDIS_CONF)
        for key in self.rds.keys('185*'):
            state = {'counter': 0, 'state': False}
            self.rds.set(key, json.dumps(state))

    def test_balancer(self):
        for item in xrange(20):
            if item < 16:
                getServer()
            else:
                self.assertRaises(socket.timeout, getServer)

    def test_open_max_links(self):
        obj = openYandex(config.KEY_ANTIGATE)
        for item in xrange(MAX_OPEN_LINKS):
            with obj.ip_port():
                data = json.loads(self.rds.get(obj.redis_key))
                self.assertEqual(data.get('counter'), item)

        with obj.ip_port():
            data = json.loads(self.rds.get(obj.redis_key))
            self.assertEqual(data['counter'], 0)

    def test_performance(self):
        pass

    def tearDown(self):
        for key in self.rds.keys('185*'):
            state = {'counter': 0, 'state': False}
            self.rds.set(key, json.dumps(state))
