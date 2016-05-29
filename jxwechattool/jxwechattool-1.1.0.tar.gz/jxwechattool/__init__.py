#!/usr/bin/env python
# coding=utf-8

__version__ = "1.1.0"


import json
import redis
import requests
import random
import logging

__all__ = ["WAccessToken", "WQRCode", "WechatException", "WJSTicket"]


REDIS_ACCESS_TOKEN_KEY = 'wechat:access_token'
WECHAT_GET_ACCESS_TOKEN_URL = "https://api.weixin.qq.com/cgi-bin/token?"\
    + "grant_type=client_credential&appid={}&secret={}"


class WechatException(Exception):
    pass


class WAccessToken(object):

    def __init__(self, app_id, app_secret, redis_access_token_key=REDIS_ACCESS_TOKEN_KEY,
                 redis_host="127.0.0.1", redis_port=6379, redis_db=0, ahead_expires_in=15 * 60):

        self.redis_pool = redis.ConnectionPool(host=redis_host, port=redis_port, db=redis_db)
        self.access_token_url = WECHAT_GET_ACCESS_TOKEN_URL.format(app_id, app_secret)
        self.redis_access_token_key = redis_access_token_key
        self.ahead_expires_in = ahead_expires_in

        if self.get_redis_client().exists(self.redis_access_token_key):
            logging.info("redis key exists: ({})".format(self.redis_access_token_key))

    def get_redis_client(self):
        return redis.StrictRedis(connection_pool=self.redis_pool)

    def fetch_access_token_info(self):
        response = requests.get(self.access_token_url)
        try:
            json_r = response.json()
        except:
            raise WechatException(u"Get Access Token Error: {}".format(response.text))

        if "errcode" in json_r:
            raise WechatException("Get Access Token Request Error: ({})".format(json_r))

        return json_r["access_token"], json_r["expires_in"]

    def _save_access_token(self, access_token, expires_in):
        client = self.get_redis_client()
        client.setex(self.redis_access_token_key, expires_in, access_token)

    def get_access_token_in_redis(self):
        access_token = self.get_redis_client().get(self.redis_access_token_key)
        if access_token:
            return access_token.decode("utf-8")

    def get_access_token(self):
        access_token = self.get_access_token_in_redis()
        if access_token:
            return access_token

        access_token, expires_in = self.fetch_access_token_info()

        #: expires_in 去掉15min
        expires_in = expires_in - 15 * 60
        self._save_access_token(access_token, expires_in)
        return access_token


WECHAT_CREATE_QRCODE_URL = "https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token={}"
WECHAT_SHOWQRCODE_URL = "https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket={}"

WECHAT_QRCODE_TEMPORARY_ACTION = "QR_SCENE"
WECHAT_QRCODE_PERMANENT_ACTION = "QR_LIMIT_SCENE"

WECHAT_QRCODE_MAX_SID_KEY = "wechat:maxsid"
WECHAT_QRCODE_MAX_SID_DEFAULT_VAL = 77
WECHAT_QRCODE_SID_KEY_PREFIX = "wechat:sid:"
WECHAT_QRCODE_M_KEY_PREFIX = "wechat:m:"
WECHAT_QRCODE_MTICKET_KEY_PREFIX = "wechat:mticket:"


class WQRCode(object):

    def __init__(self, access_token_handler, ahead_expires_in=15 * 60, temporary_expire_seconds=604800):

        self.access_token_handler = access_token_handler
        self.ahead_expires_in = ahead_expires_in
        self.temporary_expire_seconds = temporary_expire_seconds

    def _get_access_token(self):
        return self.access_token_handler.get_access_token()

    def _get_redis_client(self):
        return self.access_token_handler.get_redis_client()

    def fetch_temporary_qrcode_ticket_info(self, scene_id):
        access_token = self._get_access_token()
        data = {
            "action_name": WECHAT_QRCODE_TEMPORARY_ACTION,
            "expire_seconds": self.temporary_expire_seconds,
            "action_info": {
                "scene": {
                    "scene_id": scene_id,
                }
            }
        }

        response = requests.post(WECHAT_CREATE_QRCODE_URL.format(access_token), data=json.dumps(data))

        try:
            json_r = response.json()
        except:
            raise WechatException(u"Create QRcode Ticket Error: {}".format(response.text))

        if "errcode" in json_r:
            raise WechatException("Create QRcode Ticket Error: ({})".format(json_r))

        return json_r["ticket"], json_r["expire_seconds"], json_r["url"]

    def _get_max_scene_id(self, redis_client):
        max_sid = redis_client.get(WECHAT_QRCODE_MAX_SID_KEY)
        if not max_sid:

            sids = redis_client.keys(WECHAT_QRCODE_SID_KEY_PREFIX + "*")

            #: not exist sids
            if not sids:
                max_sid = WECHAT_QRCODE_MAX_SID_DEFAULT_VAL

            #: exist sids
            else:
                max_sid = max([int(k.split(":")[-1]) for k in sids])

            redis_client.set(WECHAT_QRCODE_MAX_SID_KEY, max_sid)

        return int(max_sid)

    def _set_max_scene_id(self, redis_client, max_sid):
        redis_client.set(WECHAT_QRCODE_MAX_SID_KEY, max_sid)

    def _set_map_in_sid_and_m(self, redis_client, sid, m, expires_in):
        redis_client.setex(WECHAT_QRCODE_SID_KEY_PREFIX + str(sid), expires_in, m)

    def _set_map_in_m_and_sid(self, redis_client, m, sid, expires_in):
        redis_client.setex(WECHAT_QRCODE_M_KEY_PREFIX + m, expires_in, sid)

    def _set_map_in_m_and_ticket(self, redis_client, m, ticket, expires_in):
        redis_client.setex(WECHAT_QRCODE_MTICKET_KEY_PREFIX + m, expires_in, ticket)

    def _get_ticket_by_m(self, redis_client, m):
        ticket = redis_client.get(WECHAT_QRCODE_MTICKET_KEY_PREFIX + m)
        if ticket:
            return ticket.decode("utf-8")

    def _get_m_by_sid(self, redis_client, sid):
        m = redis_client.get(WECHAT_QRCODE_SID_KEY_PREFIX + str(sid))
        if m:
            return m.decode("utf-8")

    def get_qrcode_url_by_m(self, val):
        client = self._get_redis_client()
        ticket_info = self._get_ticket_by_m(client, val)

        #: ticket exists
        if ticket_info:
            return WECHAT_SHOWQRCODE_URL.format(ticket_info)

        #: get max sid
        next_max_sid = self._get_max_scene_id(client) + random.randint(1, 10)

        #: get ticket
        ticket, expire_seconds, ticket_url = self.fetch_temporary_qrcode_ticket_info(next_max_sid)

        #: expires_in 去掉15min
        expires_in = expire_seconds - 15 * 60

        self._set_map_in_m_and_sid(client, val, next_max_sid, expires_in)
        self._set_map_in_sid_and_m(client, next_max_sid, val, expires_in)
        self._set_max_scene_id(client, next_max_sid)

        self._set_map_in_m_and_ticket(client, val, ticket, expires_in)

        return WECHAT_SHOWQRCODE_URL.format(ticket)

    def get_qrcode_info_by_scene_id(self, scene_id):
        client = self._get_redis_client()
        return self._get_m_by_sid(client, scene_id)


WECHAT_JSAPI_TICKET_KEY = "wechat:jsapi_ticket"
WECHAT_JSAPI_TICKET_URL = "https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token={}&type=jsapi"


class WJSTicket(object):

    def __init__(self, access_token_handler, ahead_expires_in=15 * 60):
        self.access_token_handler = access_token_handler
        self.ahead_expires_in = ahead_expires_in

    def _get_access_token(self):
        return self.access_token_handler.get_access_token()

    def _get_redis_client(self):
        return self.access_token_handler.get_redis_client()

    def _fetch_jsapi_ticket(self, access_token):
        response = requests.get(WECHAT_JSAPI_TICKET_URL.format(access_token))
        try:
            json_r = response.json()
        except Exception as e:
            logging.error((e))
            raise WechatException(u"Get jsapi_ticket Error: {}".format(response.text))

        if str(json_r.get("errcode", "0")) != "0":
            raise WechatException(u"Get jsapi_ticket Error: {}".format(json_r))

        return json_r["ticket"], json_r["expires_in"]

    def get_jsapi_ticket(self):
        jsapi_ticket = self._get_redis_client().get(WECHAT_JSAPI_TICKET_KEY)
        if jsapi_ticket:
            return jsapi_ticket.decode("utf-8")

        access_token = self._get_access_token()
        ticket, expire_seconds = self._fetch_jsapi_ticket(access_token)

        expires_in = expire_seconds - self.ahead_expires_in

        self._get_redis_client().setex(WECHAT_JSAPI_TICKET_KEY, expires_in, ticket)

        return ticket.decode("utf-8")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    access_token_handler = WAccessToken(
        app_id="wxe31fb6538d7c5976",
        app_secret="719fc21c66727cf19a71b3dbfc27d3a6")

    logging.warn(("access_token", access_token_handler.get_access_token()))

    qr_handler = WQRCode(access_token_handler)

    logging.warn(("qr ur", qr_handler.get_qrcode_url_by_m("c-8")))
    logging.warn(("info ", qr_handler.get_qrcode_info_by_scene_id(80)))

    jsapi_ticket_handler = WJSTicket(access_token_handler)

    logging.warn(("jsapi_ticket", jsapi_ticket_handler.get_jsapi_ticket()))
