#!/usr/bin/env python
#coding:utf-8
# Author        : tuxpy
# Email         : q8886888@qq.com.com
# Last modified : 2016-03-29 14:09:32
# Filename      : _adapters.py
# Description   : 
from __future__ import print_function, unicode_literals
from requests.adapters import HTTPAdapter
from dsb_requests import _api
from dsb_requests import tools
import socket

class UDPHTTPAdapter(HTTPAdapter):
    def send(self, request, timeout = None, proxies = None, **kwargs):
        proxy_node = dict(proxies)
        conn = self.get_conn_to_proxy_node(proxy_node, timeout or 1) # 进行udp打洞
        assert proxy_node, 'not has proxy_node'
        assert not proxy_node['internet']
        request.url = request.url[3:] # 删除url前的udp

    def get_conn_to_proxy_node(self, proxy_node, timeout):
        conn = tools.made_conn()
        conn.bind(('', 0))
        node_port_in_lan = _api.notify_proxy_node_access_me(proxy_node, conn)
        print('node_port_in_lan', node_port_in_lan)

