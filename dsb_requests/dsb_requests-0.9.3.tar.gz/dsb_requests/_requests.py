#!/usr/bin/env python
#coding:utf-8
# Author        : tuxpy
# Email         : q8886888@qq.com.com
# Last modified : 2016-03-17 11:10:13
# Filename      : requests.py
# Description   : 
from __future__ import print_function, unicode_literals
import requests
from dsb_requests import patch_const
reload(patch_const)
from dsb_requests import _proxy
from dsb_requests import tools
from functools import partial
import mock
import lxml.etree
import time
import re
import urlparse
import threading

if hasattr(requests, 'packages'):
    requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL'

    requests.packages.urllib3.disable_warnings() # see https://urllib3.readthedocs.org/en/latest/security.html#disabling-warnings

_proxy_manager = _proxy.ProxyManager()
_flush_lock = threading.RLock()

def flush_ip(async = True):
    last_node = _proxy_manager.last_node
    if not last_node:
        return

    if async:
        tools.async(_proxy_manager.feedback_node)(last_node)

    else:
        with _flush_lock:
            _proxy_manager.feedback_node(last_node)

class HTMLSelector(object):
    def __init__(self, response):
        self.response = response
        self._etree = None

    @property
    def etree(self):
        if self._etree is None:
            self._etree = lxml.etree.HTML(self.response.text.strip())

        return self._etree

    def get(self, xpath_rules):
        results = self.gets(tools.to_list(xpath_rules))
        return results[0] if results else None

    def gets(self, xpath_rules):
        if self.etree is None:
            return []

        for xpath_rule in tools.to_list(xpath_rules):
            _result = self.etree.xpath(xpath_rule)
            if _result:
                return _result

        return []

def _add_proxies_param(kwargs):
    proxy_node = _proxy_manager.get_best_proxy_node()
    if proxy_node:
        proxy_url = 'http://{username}:{password}@{ip}:{port}'.format(
                **proxy_node)
        kwargs['proxies'] = {
            'http'  :   proxy_url,
            'https' :   proxy_url,
            }

    else:
        kwargs.pop('proxies', None)

    return kwargs

def _need_proxy_this_url(url, proxy_domain_rules):
    """根据url判断该url是否需要走代理"""
    if not proxy_domain_rules:
        return True

    for proxy_domain_rule in tools.to_list(proxy_domain_rules):
        if re.search(proxy_domain_rule, url):
            return True

    return False

def request(method, url, *args, **kwargs):
    """
    session: 指定使用哪个session, 不指定则表示使用requests
    retry: 重试多少次， 默认2次
    retry_interval: 重试间隔, 默认0
    proxy_domain: 只对部分域名做代理，写正则表达式即可, 可以传入string, tuple, list
    """
    session = kwargs.pop('session', requests)
    retry = kwargs.pop('retry', int(REQUEST_RETRY))
    proxy_domain = kwargs.pop('proxy_domain', None)

    retry_interval = kwargs.pop('retry_interval', int(REQUEST_RETRY_INTERVAL))

    if _need_proxy_this_url(url, proxy_domain):
        kwargs.setdefault('timeout', (2, 10))
        _add_proxies_param(kwargs)

    _ex_counter = 0
    _proxy_ex_counter = 0
    response = None
    proxy_has_error = False
    while True:
        try:
            response = session.request(method, url, *args, **kwargs)
            _proxy_manager.incr_use_counter()

        except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout) as ex:
            _add_proxies_param(kwargs)
            continue

        except requests.exceptions.RequestException as ex:
            if 'ProxyError' in str(ex.message) and _proxy_ex_counter < PROXY_RETRY: # 允许重试几次由于代理出错的情况
                if 'timed out' not in str(ex.message): # 如果是超时了，就不理，表示已经有重拨过了
                    _proxy_manager.flush_cache()

                else:
                    print('__________', str(ex.message))

                _proxy_ex_counter += 1
                _add_proxies_param(kwargs)
                continue

            _ex_counter += 1
            if _ex_counter > retry:
                raise

            retry_interval and time.sleep(retry_interval)
            continue

        break

    response.selector = HTMLSelector(response)

    return response

get = partial(request, 'GET')
post = partial(request, 'POST')
delete = partial(request, 'DELETE')
put = partial(request, 'PUT')

import unittest
class TestCase(unittest.TestCase):
    @mock.patch.object(_proxy_manager, 'get_best_proxy_node')
    def test_has_proxy_node(self, mock_get_best_proxy_node):
        mock_get_best_proxy_node.return_value = {
                'ip'            :           '123.123.123.123',
                'port'          :           '1234',
                'username'      :           'ljd',
                'password'      :           'dsb',
                }

        kwargs = {}
        _add_proxies_param(kwargs)

        self.assertIn('proxies', kwargs)
        self.assertEqual(kwargs['proxies']['http'],
                'http://ljd:dsb@123.123.123.123:1234')

    @mock.patch.object(_proxy_manager, 'get_best_proxy_node')
    def test_no_proxy_node(self, mock_get_best_proxy_node):
        mock_get_best_proxy_node.return_value = None
        kwargs = {}
        _add_proxies_param(kwargs)
        self.assertNotIn('proxies', kwargs)

    def test_need_proxy_this_url(self):
        self.assertFalse(_need_proxy_this_url('http://www.baidu.com', r'.+\.taobao.com'))
        self.assertTrue(_need_proxy_this_url('http://www.taobao.com', r'.+\.taobao.com'))

