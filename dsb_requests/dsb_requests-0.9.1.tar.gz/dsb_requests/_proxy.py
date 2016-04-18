#!/usr/bin/env python
#coding:utf-8
# Author        : tuxpy
# Email         : q8886888@qq.com.com
# Last modified : 2016-03-19 14:25:22
# Filename      : _proxy.py
# Description   : 
from __future__ import print_function, unicode_literals
import requests
from dsb_requests import patch_const
reload(patch_const)
from dsb_requests import _api
import socket
import time

class ProxyManager(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            _instance = object.__new__(cls, *args, **kwargs)
            cls.__init__(_instance, *args, **kwargs)
            cls._instance = _instance

        return cls._instance

    def __init__(self):
        self._last_node = None
        self._node_use_counter = 0
        self.max_node_use = int(NODE_CACHE_COUNTER)

    @property
    def node_use_counter(self):
        if not self._last_node:
            self._node_use_counter = 0

        return self._node_use_counter

    def get_cache_node(self):
        if not self._last_node:
            return None

        if self.node_use_counter > int(NODE_CACHE_COUNTER):
            return None

        return self._last_node

    @property
    def last_node(self):
        return self._last_node

    @last_node.setter
    def last_node(self, node):
        self._last_node = node
        self._node_use_counter = 0

    def feedback_node(self, node):
        """把这个节点告诉服务器，需要更换了"""
        _api.feedback_node(node['ip'], node['username'], node['password'])
        self.flush_cache()

    def incr_use_counter(self):
        self._node_use_counter += 1

    def flush_cache(self):
        self._last_node = None
        self._node_use_counter = 0

    def get_best_proxy_node(self):
        cache_node = self.get_cache_node()
        if cache_node and self.node_use_counter <= self.max_node_use:
            return cache_node

        nodes = _api.fetch_proxy_node_response()
        if not nodes:
            return None

        alive_nodes = []
        for node in nodes:
            try:
                node['delay'] = self.get_node_delay(node)
                alive_nodes.append(node)

            except socket.error as ex:
                continue

        if not alive_nodes:
            return 

        best_node = min(alive_nodes, key = lambda node: node['delay'])

        self.last_node = best_node
        return best_node

    def get_node_delay(self, node):
        begin_time = time.time()
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        test_socket.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
        test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        test_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

        test_socket.settimeout(1)
        test_socket.connect((node['ip'], node['port']))
        delay = time.time() - begin_time
        test_socket.close()

        return delay

