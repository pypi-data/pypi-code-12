# -*- coding: utf-8 -*-
"""
    beecloud.utils
    ~~~~~~~~~
    This module contains common utils.
    :created by xuanzhui on 2015/12/24.
    :copyright (c) 2015 BeeCloud.
    :license: MIT, see LICENSE for more details.
"""

from beecloud.entity import BCResult, BCReqType
from beecloud import BEECLOUD_HOSTS, BEECLOUD_RESTFUL_VERSION, NETWORK_ERROR_CODE, NETWORK_ERROR_NAME, \
    NOT_SUPPORTED_CODE, NOT_SUPPORTED_NAME
import random
import datetime
import requests
import requests.exceptions
import sys
import hashlib
import time
import json

if sys.version_info[0] == 3:   # if 3
    import urllib.parse
    long = int
else:
    import urllib


URL_REQ_SUCC = 1
URL_REQ_FAIL = 0


def get_random_host():
    return BEECLOUD_HOSTS[random.randint(0, len(BEECLOUD_HOSTS)-1)] + BEECLOUD_RESTFUL_VERSION


def obj_to_dict(obj):
    return {k: v for (k, v) in obj.__dict__.items() if v is not None}


def order_num_on_datetime():
    # py2 %f 后三位在win经常为0
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3:]


def _http_req_with_params(url, obj, method='POST', timeout=None):
    if type(obj) is not dict:
        req_param = obj_to_dict(obj)
    else:
        req_param = obj

    try:
        if method == 'POST':
            http_resp = requests.post(url, json=req_param, timeout=timeout)
        elif method == 'PUT':
            http_resp = requests.put(url, json=req_param, timeout=timeout)
        else:
            raise ValueError('method [{:s}] is not supported'.format(method))
    except requests.exceptions.ConnectionError:
        return _deal_with_conn_error()

    if http_resp.status_code == 200:
        http_resp.encoding = 'UTF-8'
        return URL_REQ_SUCC, http_resp.json()
    else:
        return _deal_with_invalid_resp(http_resp)


def http_post(url, obj, timeout=None):
    """
    http post request
    :param url: post url
    :param obj: post param
    :param timeout: refer to desc of BCApp timeout
    :return: tuple, [0] indicate the result code: 0 means failure, 1 means success; [1] is beecloud.entity.BCResult
    """
    return _http_req_with_params(url, obj, timeout=timeout)


def http_put(url, obj, timeout=None):
    """
    http put request
    :param url: put url
    :param obj: put param
    :param timeout: refer to desc of BCApp timeout
    :return: tuple, [0] indicate the result code: 0 means failure, 1 means success; [1] is beecloud.entity.BCResult
    """
    return _http_req_with_params(url, obj, method='PUT', timeout=timeout)


def obj_to_quote_str(param_obj):
    str_tmp = json.dumps(obj_to_dict(param_obj))
    if sys.version_info[0] == 3:
        return urllib.parse.quote_plus(str_tmp)
    else:
        return urllib.quote_plus(str_tmp)


def http_get(url, timeout=None):
    """
    http get request
    :param url: url with params concatenated
    :param timeout: refer to desc of BCApp timeout
    :return: tuple, [0] indicate the result code: 0 means failure, 1 means success; [1] is beecloud.entity.BCResult
    """
    try:
        http_resp = requests.get(url, timeout=timeout)
    except requests.exceptions.ConnectionError:
        return _deal_with_conn_error()

    if http_resp.status_code == 200:
        http_resp.encoding = 'UTF-8'
        return URL_REQ_SUCC, http_resp.json()
    else:
        return _deal_with_invalid_resp(http_resp)


def _deal_with_conn_error():
    resp = BCResult()
    resp.result_code = NETWORK_ERROR_CODE
    resp.result_msg = NETWORK_ERROR_NAME
    resp.err_detail = 'ConnectionError: normally caused by timeout'
    return URL_REQ_FAIL, resp


def _deal_with_invalid_resp(http_resp):
    resp = BCResult()
    resp.result_code = NETWORK_ERROR_CODE
    resp.result_msg = http_resp.status_code
    resp.err_detail = http_resp.reason
    return URL_REQ_FAIL, resp


def set_common_attr(resp_dict, bc_result):
    bc_result.result_code = resp_dict.get('result_code')
    bc_result.result_msg = resp_dict.get('result_msg')
    bc_result.err_detail = resp_dict.get('err_detail')


def report_not_supported_err(method_name):
    err_result = BCResult()
    err_result.result_code = NOT_SUPPORTED_CODE
    err_result.result_msg = NOT_SUPPORTED_NAME
    err_result.err_detail = u'[{:s}] does NOT support test mode currently!'.format(method_name)
    return err_result


def local_timestamp_since_epoch(dt):
    """
    :param dt: datetime which should be set with system local timezone
    :return: milliseconds from epoch 1970-01-01 00:00:00 UTC
    """
    epoch = datetime.datetime.utcfromtimestamp(0)
    # e.g. Beijing timezone is 8 hours faster than UTC
    delta = dt - epoch - (datetime.datetime.now() - datetime.datetime.utcnow())
    return long((delta.days * 86400 + delta.seconds) * 1000 + delta.microseconds / 1000)


def attach_app_sign(req_param, req_type, bc_app):
    # BC APP的唯一标识
    if not bc_app.app_id:
        raise ValueError('app id is not set')

    req_param.app_id = bc_app.app_id

    # 签名生成时间
    # 时间戳, 毫秒数
    timestamp = long(time.time()*1000)
    req_param.timestamp = timestamp

    # 加密签名
    # 算法: md5(app_id+timestamp+secret), 32位16进制格式, 不区分大小写
    if bc_app.is_test_mode:
        if not bc_app.test_secret:
            raise ValueError('test secret is not set')
        else:
            req_param.app_sign = hashlib.md5((bc_app.app_id + str(timestamp) +
                                              bc_app.test_secret).encode('UTF-8')).hexdigest()
    else:
        if req_type in (BCReqType.REFUND, BCReqType.TRANSFER):
            if not bc_app.master_secret:
                raise ValueError('master secret is not set')
            else:
                req_param.app_sign = hashlib.md5((bc_app.app_id + str(timestamp) +
                                                  bc_app.master_secret).encode('UTF-8')).hexdigest()
        else:
            if not bc_app.app_secret:
                raise ValueError('app secret is not set')
            else:
                req_param.app_sign = hashlib.md5((bc_app.app_id + str(timestamp) +
                                                  bc_app.app_secret).encode('UTF-8')).hexdigest()

wx_oauth_url_basic = 'https://open.weixin.qq.com/connect/oauth2/authorize?'
wx_sns_token_url_basic = 'https://api.weixin.qq.com/sns/oauth2/access_token?'


# 获取code 的url生成规则，redirect_url是微信用户登录后的回调页面，将会有code的返回
def fetch_code(wx_app_id, redirect_url):
    code_data = {}
    code_data['appid'] = wx_app_id
    code_data['redirect_uri'] = redirect_url
    code_data['response_type'] = 'code'
    code_data['scope'] = 'snsapi_base'
    code_data['state'] = 'STATE#wechat_redirect'
    if sys.version_info[0] == 3:
        params = urllib.parse.urlencode(code_data)
    else:
        params = urllib.urlencode(code_data)
    return wx_oauth_url_basic + params


# 获取openid的url生成方法
def create_fetch_open_id_url(wx_app_id, wx_app_secret, code):
    fetch_data = {}
    fetch_data['appid'] = wx_app_id
    fetch_data['secret'] = wx_app_secret
    fetch_data['grant_type'] = 'authorization_code'
    fetch_data['code'] = code
    if sys.version_info[0] == 3:
        params = urllib.parse.urlencode(fetch_data)
    else:
        params = urllib.urlencode(fetch_data)
    return wx_sns_token_url_basic + params


def fetch_open_id(wx_app_id, wx_app_secret, code):
    url = create_fetch_open_id_url(wx_app_id, wx_app_secret, code)
    http_response = requests.get(url)
    if http_response.status_code == 200:
        resp_dict = http_response.json()
        return resp_dict.get('openid')
    else:
        return ''
