# -*- coding: utf-8 -*-

import json
import requests


class MSG91Exception(Exception):

    def __init__(self, message):
        self.message = message

    def get_message(self):
        return self.message


class MSG91Client(object):
    """A simple API client for the msg91 & sendOTP APIs combined.

    It includes methods for calling sms api of msg91
    and methods for calling sendOTP APIs.

    Both the API clients are combined as one for the sake of
     brevity and simplicity.

    If you only want to send SMSs then you can just pass api key
    at the time of instantiating and start making use of send sms methods.

    In order to use otp APIs you will need to pass app_key  too.
    ref. https://github.com/SendOTP/SendOTPAndroid and
    http://help.msg91.com/article/181-how-to-generate-key-hash-for-android
    """

    def __init__(self, api_key, app_key=None, **kwargs):
        self.auth_key = api_key
        self.app_key = app_key

        self.sender_id = kwargs.get('sender_id') or 'MSGIND'
        self.route = kwargs.get('route') or 4

        self.sms_url = 'https://control.msg91.com/api/sendhttp.php'
        self.otp_base_url = 'https://sendotp.msg91.com/api'
        self.otp_ops = {'otp': 'generateOTP',
                        'status': 'checkStatus',
                        'verify': 'verifyOTP'}

    def _get_otp_url(self, op):
        return '/'.join([self.otp_base_url, self.otp_ops[op]])

    def _get_app_key_headers(self):
        if self.app_key is None:
            raise MSG91Exception('App Key is not set.')

        return {'application-key': self.app_key,
                'content-type': 'application/json'}

    def generate_otp(self, mobile_number, country=91):
        url = self._get_otp_url('otp')

        payload = {'countryCode': str(country),
                   'mobileNumber': str(mobile_number),
                   'getGeneratedOTP': True}

        res = requests.post(url, data=json.dumps(payload),
                            headers=self._get_app_key_headers())

        if res.status_code != requests.codes.ok:
            raise MSG91Exception('Error {}'.format(res.status_code))

        return json.loads(res.content)

    def verify_otp(self, mobile_number, otp, country=91):
        url = self._get_otp_url('verify')
        payload = {'countryCode': str(country),
                   'mobileNumber': str(mobile_number),
                   'oneTimePassword': str(otp)}

        res = requests.post(url,
                            data=json.dumps(payload),
                            headers=self._get_app_key_headers())

        if res.status_code != requests.codes.ok:
            raise MSG91Exception('Error {}'.format(res.status_code))

        return json.loads(res.content)

    def check_otp_status(self, mobile, refresh_token, country=91):
        res = requests.get(self._get_otp_url('status'),
                           params={'mobileNumber': mobile,
                                   'countryCode': country,
                                   'refreshToken': refresh_token},
                           headers=self._get_app_key_headers())

        if res.status_code != requests.codes.ok:
            raise MSG91Exception('Error {}'.format(res.status_code))

        return json.loads(res.content)

    def send_sms(self, message, mobile, country=91):
        res = requests.get(self.sms_url,
                           params={'authkey': self.auth_key,
                                   'mobiles': mobile,
                                   'message': message,
                                   'sender': self.sender_id,
                                   'route': self.route,
                                   'country': country,
                                   'response': 'json'})
        if res.status_code != requests.codes.ok:
            raise MSG91Exception('Error {}'.format(res.status_code))

        return json.loads(res.content)

    def send_sms_bulk(self, message, country=91, *recipients):
        mobiles = ','.join(str(num) for num in recipients)

        res = requests.get(self.sms_url,
                           params={'authkey': self.auth_key,
                                   'mobiles': mobiles,
                                   'message': message,
                                   'sender': self.sender_id,
                                   'route': self.route,
                                   'country': country,
                                   'response': 'json'})

        if res.status_code != requests.codes.ok:
            raise MSG91Exception('Error {}'.format(res.status_code))

        return json.loads(res.content)