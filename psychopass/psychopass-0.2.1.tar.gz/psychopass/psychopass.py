#!/usr/bin/env python
# coding: utf-8
# File Name: psychopass.py
# Author: cissoid
# Created At: 2016-06-28T12:06:00+0800
# Last Modified: 2016-06-28T12:06:13+0800
from __future__ import absolute_import, division, print_function, unicode_literals
import argparse
import hashlib
import hmac

from future.builtins import bytes

from .flowerpass import flowerpass

__all__ = ['psychopass']

DEFAULT_LENGTH = 20
USE_SPECIAL_CHARS = True
SPECIAL_CHARS = '~!@#$%^&?'
SPECIAL_CHARS_STEP = 3
UPPERCASE_STEP = 2


def psychopass(passwd, salt, length=DEFAULT_LENGTH, special_chars=USE_SPECIAL_CHARS):
    source, rule = _hash_passwd(passwd, salt)
    source = list(source)
    if special_chars:
        source = _add_special_chars(source, rule)
    source = _uppercase(source, rule)
    return ''.join(source)[:length]


def _hash_passwd(passwd, salt):
    tmp = _hmac_encode(passwd, salt)
    source = _hmac_encode(passwd, tmp)
    rule = _hmac_encode(salt, tmp)
    return source, rule


def _hmac_encode(key, msg):
    # Ensure arguments are bytes, for compatibles.
    if not isinstance(key, bytes):
        key = bytes(key, encoding='utf8')
    if not isinstance(msg, bytes):
        msg = bytes(msg, encoding='utf8')
    return hmac.new(key, msg, digestmod=hashlib.sha1).hexdigest()


def _add_special_chars(source, rule):
    for i, c in enumerate(rule):
        if i in (0, len(rule) - 1):
            continue
        if (i + ord(c)) % SPECIAL_CHARS_STEP == 0:
            source[i] = SPECIAL_CHARS[(i + ord(c)) % len(SPECIAL_CHARS)]
    return source


def _uppercase(source, rule):
    for i, c in enumerate(rule):
        if (i + ord(c)) % UPPERCASE_STEP == 0 and source[i].isalpha():
            source[i] = source[i].upper()
    return source


def _parse_command_arguments():
    parser = argparse.ArgumentParser(
        description='Password generator inspired by flowerpassword.')
    parser.add_argument('-p', '--passwd', required=True,
                        dest='passwd', help='The original password.')
    parser.add_argument('-k', '--key', required=True,
                        dest='key', help='The key used for encrypto.')
    parser.add_argument('-l', '--length', dest='length', type=int,
                        default=DEFAULT_LENGTH, help='Max length of generated password.')
    parser.add_argument('--no-special-chars', dest='special_chars', action='store_false',
                        help='Don\'t add special characters to generated password.')
    parser.add_argument('--flower', dest='flowerpass', action='store_true',
                        help='Use flowerpassword compitable algorithm.')
    options = parser.parse_args()
    return options


def main():
    options = _parse_command_arguments()
    if options.flowerpass:
        print(flowerpass(options.passwd, options.key))
    else:
        print(psychopass(options.passwd, options.key,
                         options.length, options.special_chars))

if __name__ == '__main__':
    main()
