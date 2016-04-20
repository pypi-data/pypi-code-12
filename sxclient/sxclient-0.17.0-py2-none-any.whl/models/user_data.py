'''
Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: Apache 2.0, see LICENSE for more details.
'''
import os
import hashlib

import bcrypt

from sxclient.tools import toutf8
from sxclient.exceptions import InvalidUserKeyError
from sxclient.defaults import (
    VALID_DECODED_KEY_LENGTH,
    VALID_ENCODED_KEY_LENGTH,
    VALID_ENCODED_KEY_CHARACTERS,
)

__all__ = ['UserData']


class UserData(object):
    '''
    Prepare user access data.

    In addition to the default initialization, the following class methods can
    be used to initialize the object:
      - from_key;
      - from_key_path;
      - from_userpass_pair.

    For example, to initialize the object based on username and password, run:
        UserData.from_userpass_pair(username, password, uuid)
    '''

    def __init__(self, dec_key):
        if len(dec_key) != VALID_DECODED_KEY_LENGTH:
            raise InvalidUserKeyError('Invalid decoded user key length')
        self._key = dec_key

    @property
    def key(self):
        return self._key

    @property
    def uid(self):
        return self._key[:20]

    @property
    def secret_key(self):
        return self._key[20:40]

    @property
    def padding(self):
        return self._key[40:42]

    @classmethod
    def from_key(cls, enc_key):
        '''Prepare user access data using base64-encoded user key.'''
        dec_key = cls._decode_key(enc_key)
        return cls(dec_key)

    @classmethod
    def from_key_path(cls, key_path):
        '''
        Prepare user access data using path to the file containing
        base64-encoded user key.
        '''
        key_path = os.path.expanduser(key_path)
        enc_key = cls._load_key(key_path)
        dec_key = cls._decode_key(enc_key)
        return cls(dec_key)

    @classmethod
    def from_userpass_pair(cls, username, password, cluster_uuid):
        '''
        Prepare user access data based on username, password and cluster UUID.

        Note that username and password should be encoded in UTF-8.
        '''
        username = toutf8(username)
        password = toutf8(password)

        # prepare uid
        sha1 = hashlib.sha1()
        sha1.update(username)
        uid = sha1.digest()

        # prepare salt for password hashing
        sha1 = hashlib.sha1()
        sha1.update(cluster_uuid)
        sha1.update(username)
        salt = sha1.digest()[:16]
        encsalt = bcrypt.encode_salt(salt, 12)

        # prepare hashed password with '2b' prefix
        hashpw = bcrypt.hashpw(password, encsalt)
        hashpw = '$2b' + hashpw[3:]

        # prepare secret key
        sha1 = hashlib.sha1()
        sha1.update(cluster_uuid)
        sha1.update(hashpw)
        secret = sha1.digest()

        padding = '\x00\x00'
        dec_key = ''.join([uid, secret, padding])
        return cls(dec_key)

    @staticmethod
    def _load_key(path):
        '''Read base64-encoded key from 'path'.'''
        with open(path, 'rb') as keyfile:
            enc_key = keyfile.read(VALID_ENCODED_KEY_LENGTH)
        return enc_key

    @staticmethod
    def _decode_key(enc_key):
        '''Verify and decode base64-encoded key.'''
        if len(enc_key) != VALID_ENCODED_KEY_LENGTH:
            raise InvalidUserKeyError('Invalid base64-encoded user key length')

        # Python 2.7.10 documentation incorrectly states that
        # 'base64.b64decode' raises 'TypeError' in case of invalid input
        # characters. In reality, invalid input characters are silently
        # ignored. The issue has been reported in
        #   https://bugs.python.org/issue22088
        # Input validity is checked independently of 'base64.b64decode', below.
        invalid_char_in_key = any(
            char not in VALID_ENCODED_KEY_CHARACTERS for char in enc_key
        )
        if invalid_char_in_key:
            raise InvalidUserKeyError(
                'Invalid character in base64-encoded user key'
            )

        dec_key = enc_key.decode('base64')
        return dec_key
