# -*- coding: utf-8 -*-
__author__ = 'tangke'
import re
from string import Template

import requests
import simplejson

from MosT.log import MyLog
from datacontext import DataContext


class RequestObject(object):
    def __init__(self, url, headers, params, params_type=None, method_type=None, **kwargs):
        self.url = url
        self.headers = headers
        self.params = params
        self.params_type = params_type
        self.method = method_type

def send_http(case_obj):
    if case_obj.method == 'post':
        post(case_obj.url, case_obj.headers, case_obj.params, case_obj.params_type)
    else:
        get(case_obj.url, case_obj.headers, case_obj.params)


def post(url, headers, params, params_type=None, **kwargs):
    '''
    定义post请求
    '''
    if params_type is not None:
        params = simplejson.loads(params)
    MyLog.log().info('发送post请求,url是:' + url)
    result = requests.post(_fortmat_url(url), headers=_format_header(headers), data=params, **kwargs).text
    #MyLog.log().debug('post请求返回结果是:' + result).text


def get(url, headers, params, **kwargs):
    '''
    定义get请求
    '''
    MyLog.log().info('发送get请求,url是:' + url)
    result = requests.get(_fortmat_url(url), headers=_format_header(headers), params=params, **kwargs).text
    #MyLog.log().debug('get请求返回结果是:' + result)


def _format_header(header_dict):
    '''
    格式化Header
    '''
    print type(header_dict)
    if  header_dict == "":
        return None
    if not isinstance(header_dict, basestring):
        header_dict = str(header_dict)
    return simplejson.loads(_format(header_dict))


def _fortmat_url(url):
    return _format(url)


def _format(base_string):
    temp_dict = {}
    template = Template(base_string)
    for pattern in re.findall(r'\$\w+', base_string):
        _attr = pattern.replace('$', '')
        if hasattr(DataContext, _attr):
            temp_dict[_attr] = getattr(DataContext, _attr)
    return template.substitute(temp_dict)


if __name__ == '__main__':
    pass