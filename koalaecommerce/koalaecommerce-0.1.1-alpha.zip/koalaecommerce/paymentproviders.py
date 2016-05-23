# -*- coding: utf-8 -*-
"""
    koalaecommerce.paymentproviderss.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    Koala ecommerce payment providers. This is a really basic set of implementation for handling offline payments.

    :copyright: (c) 2015 Lighthouse
    :license: LGPL
"""
from Crypto.Cipher import AES
from Crypto import Random
import unicodedata
from urllib import urlencode
from urlparse import urlparse, urlunparse, parse_qs, parse_qsl


BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[0:-ord(s[-1])]


class AESCipher:
    def __init__(self, key):
        """
        Requires hex encoded param as a key
        """
        self.key = key.decode("hex")

    def encrypt(self, raw, iv=None):
        """
        Returns hex encoded encrypted value!
        :param iv:
        :param raw:
        """
        # raw.decode('ascii')
        # raw.encode('utf-8')
        raw = unicodedata.normalize('NFKD', raw).encode('ascii', 'ignore')
        if not iv:
            iv = Random.new().read(AES.block_size)

        raw = pad(raw)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return cipher.encrypt(raw).encode("hex").upper()

    def decrypt(self, enc, iv=None):
        """
        Requires hex encoded param to decrypt
        :param enc:
        :param iv:
        """
        enc = enc.decode("hex")
        if not iv:
            iv = enc[:16]
        # enc = enc[16:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(enc))


def encrypt_payload(payload, vendor_key, iv):
    aes = AESCipher(vendor_key.encode("hex"))
    return '@' + aes.encrypt(raw=payload, iv=iv)


def decrypt_payload(payload, vendor_key):
    payload = payload.replace("@", "", 1)
    aes = AESCipher(vendor_key.encode("hex"))
    return aes.decrypt(enc=payload, iv=vendor_key)


def _offline_payment_request_parser(encrypted_payload, provider_config):
    raw_request_payload = decrypt_payload(payload=encrypted_payload, vendor_key=provider_config['encryption_key'])
    request_payload = dict(parse_qsl(raw_request_payload))

    response_payload = {
        'Status': 'OK',
        'OrderRef': request_payload['OrderRef'],
        'Amount': request_payload['Amount'],
    }
    response_payload_str = unicode(urlencode(response_payload))

    u = urlparse(request_payload['SuccessURL'])
    query = parse_qs(u.query)
    query['encrypted_payload'] = encrypt_payload(payload=response_payload_str, vendor_key=provider_config['encryption_key'], iv=provider_config['encryption_key'])
    u = u._replace(query=urlencode(query, True))
    return urlunparse(u)


class BACS(object):
    @classmethod
    def process(cls, encrypted_payload, provider_config, **kwargs):
        return _offline_payment_request_parser(encrypted_payload=encrypted_payload, provider_config=provider_config)


class Cheque(object):
    @classmethod
    def process(cls, encrypted_payload, provider_config, **kwargs):
        return _offline_payment_request_parser(encrypted_payload=encrypted_payload, provider_config=provider_config)
