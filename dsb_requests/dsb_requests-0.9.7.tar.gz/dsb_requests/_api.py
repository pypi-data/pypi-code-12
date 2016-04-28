#!/usr/bin/env python
#coding:utf-8
# Author        : tuxpy
# Email         : q8886888@qq.com.com
# Last modified : 2016-03-17 11:13:35
# Filename      : api.py
# Description   : 
from __future__ import print_function, unicode_literals
import requests
from dsb_requests import logs
from dsb_requests import patch_const
reload(patch_const)
import random
import time
import socket

def _request(method, url, data = None):
    try:
        response = requests.request(method, 
                'http://{hostname}:{port}{url}'.format(
                    hostname = API_HOSTNAME, port = API_PORT, url = url), 
                headers = {
                    'dsb_client_key'    :       DSB_CLIENT_KEY,
                    }, 
                data = data)

        if response.json()['status_code'] != 0:
            logs.print_error(response.json()['status_msg'] or 'error')
            return

        return response

    except requests.exceptions.RequestException:
        return None


def fetch_proxy_node_response():
    """获取所有可用的节点信息"""
    response = _request('GET', '/api/proxy/node')
    if not response:
        return []

    nodes = response.json()['nodes']
    return nodes

def feedback_node(node_ip, username, password):
    _request('PUT', '/api/proxy/node', data = {
        'node_ip'       :       node_ip,
        'username'      :       username,
        'password'      :       password,
        })

