#!/bin/env python
#-*- encoding=utf8 -*-
#
# Copyright 2013 beager
#
# 作者：zone
#
# 功能：该模块提供RSA加解密功能
#
# 版本：V1.0.0
import Crypto.PublicKey.RSA as RSA
import binascii

from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import MD5, SHA
import base64


_n = 6048566640982814036867974748944650758462510523773744160069659405889316028964734184181273868341724783394669858519314451621417501926573879514089468871950113
_e = 65537l
_d = 4371429252943390555812008849714869206319740161413299237708461140423691253977250964915490307689149820147397001025731551470098589039498607233729178552063973

"""
rsa 加密和解密
使用方法:
    from beager_utils import rsa

    encrypted = rsa.encrypt('plain_value')
    rsa.decrypt(encrypted)

"""
def encrypt(data, n=_n, e=_e):
    key = RSA.construct((n, e))
    return binascii.hexlify(key.encrypt(data, '')[0])

def decrypt(data, n=_n, e=_e, d=_d):
    key = RSA.construct((n, e, d))
    return key.decrypt(binascii.unhexlify(data))


"""
rsa 签名
    from beager_utils import rsa

    # 将 msg 先用 md5 哈希,然后再签名
    signed_msg = rsa.sign('somekey', 'somemessage', 'md5')

    # 将 msg 先用 SHA 哈希,然后再签名
    signed_msg = rsa.sign('somekey', 'somemessage', 'md5')

    # 需要验证的信息是用 md5 哈希的
    rsa.verify('somekey', signed_msg, 'md5')

    # 需要验证的信息是用 sha 哈希的
    rsa.verify('somekey', signed_msg, 'sha')

"""
def sign(key, msg, method):
    key_obj = RSA.importKey(key)
    hash_val = _hash(msg, method)
    signer = PKCS1_v1_5.new(key_obj)
    return base64.b64encode(signer.sign(hash_val))

def verify(key, msg, method, signature):
    hash_val = _hash(msg, method)
    key_obj = RSA.importKey(key)
    signer = PKCS1_v1_5.new(key_obj)
    return signer.verify(hash_val, base64.b64decode(signature))

def _hash(msg, method):
    method = method.upper()
    if method == 'MD5':
        return MD5.new(msg)
    elif method == 'SHA':
        return SHA.new(msg)
    else:
        return msg