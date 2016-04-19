# -*- coding: utf-8 -*-
"""
SMS backend of http://www.yuntongxun.com/
"""
import datetime
import base64
import urllib2
import json
from hashlib import md5

from .. import app_settings
from .base import BaseSmsBackend


class SmsBackend(BaseSmsBackend):
    def __init__(self, *args, **kwargs):
        # Server ip
        self.server_ip = app_settings.YTX_SERVER_IP
        # Server port
        self.server_port = app_settings.YTX_SERVER_PORT
        # Rest version
        self.soft_version = app_settings.YTX_REST_VERSION
        # Account sid
        self.account_sid = app_settings.YTX_ACCOUNT_SID
        # Account token
        self.account_token = app_settings.YTX_ACCOUNT_TOKEN
        # Application id
        self.app_id = app_settings.YTX_APP_SID

        self.collection = None

        super(SmsBackend, self).__init__(*args, **kwargs)

    def init_request(self):
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        signature = md5(('%s%s%s' % (self.account_sid, self.account_token, timestamp))).hexdigest().upper()
        url = 'https://%s:%s/%s/Accounts/%s/SMS/TemplateSMS?sig=%s' % (
            self.server_ip, self.server_port, self.soft_version, self.account_sid, signature)
        auth = base64.encodestring(('%s:%s' % (self.account_sid, timestamp))).strip()

        req = urllib2.Request(url)
        req.add_header("Accept", "application/json")
        req.add_header("Content-Type", "application/json;charset=utf-8")
        req.add_header("Authorization", auth)

        return req

    def get_body(self, message):
        key = message['params']['key']
        expire_minutes = message['params']['expire_minutes']

        body = {
            'to': ','.join(message['to']),
            'datas': [key, expire_minutes],
            'templateId': '1',
            'appId': self.app_id
        }

        return json.dumps(body)

    def open(self, req):
        self.collection = urllib2.urlopen(req)

    def close(self):
        if self.collection:
            self.collection.close()

    def send(self, message):
        req = self.init_request()
        body = self.get_body(message)
        req.add_data(body)
        self.open(req)
        result = self.collection.read()
        return result

    def send_messages(self, messages):
        if not messages:
            return 0

        try:
            for message in messages:
                self.send(message)
        finally:
            self.close()

        return len(messages)
