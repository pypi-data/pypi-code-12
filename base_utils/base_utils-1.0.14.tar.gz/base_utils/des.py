#!/bin/env python
#-*- encoding=utf8 -*-

import pyDes
import binascii

_des_key = 'Hnnr&z4U'
_des_iv = 'g&fuq7yt'

_k = pyDes.des(key = _des_key, mode = pyDes.CBC , IV = _des_iv , pad = None, padmode = pyDes.PAD_PKCS5)

"""
des加密和解密
使用方法:
    from base_utils import des

    encrypted = des.encrypt('plain_value')
    des.decrypt(encrypted)

"""

def encrypt(d):
    """ 加密
    """
    return binascii.hexlify( _k.encrypt(d) )

def decrypt(e):
    """ 解密
    """
    return _k.decrypt( binascii.unhexlify(e) )