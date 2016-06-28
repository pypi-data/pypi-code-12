#!/usr/bin/env python
# coding: utf-8
# File Name: flowerpass.py
# Author: cissoid
# Created At: 2016-06-28T12:05:33+0800
# Last Modified: 2016-06-28T12:05:51+0800
from __future__ import absolute_import, division, print_function, unicode_literals
import argparse
import hmac

from future.builtins import bytes

__all__ = ['flowerpass']


def flowerpass(passwd, salt):
    source, rule = _hash_passwd(salt, passwd)
    passwd = _upper_passwd(source, rule)
    passwd = _trick_no_number_header(passwd)
    return passwd[:16]


def _hash_passwd(passwd, salt):
    tmp = _hmac_encode(passwd, salt)
    source = _hmac_encode('snow', tmp)
    rule = _hmac_encode('kise', tmp)
    return source, rule


def _hmac_encode(key, msg):
    if not isinstance(key, bytes):
        key = bytes(key, encoding='utf8')
    if not isinstance(msg, bytes):
        msg = bytes(msg, encoding='utf8')
    return hmac.new(key, msg).hexdigest()


def _upper_passwd(source, rule):
    uppers = set('sunlovesnow1990090127xykab')
    passwd = list(source)
    for i, c in enumerate(passwd):
        if c.isdigit():
            continue
        if rule[i] in uppers:
            passwd[i] = passwd[i].upper()
    return ''.join(passwd)


def _trick_no_number_header(passwd):
    if passwd[0].isdigit():
        return 'K' + passwd[1:]
    return passwd


def _parse_command_arguments():
    parser = argparse.ArgumentParser(
        description='An Python implemention of http://www.flowerpassword.com/.')
    parser.add_argument('-p', '--passwd', required=True, dest='passwd',
                        help='The original password.')
    parser.add_argument('-k', '--key', required=True, dest='key',
                        help='The key used for encrypto.')
    options = parser.parse_args()
    return options


def main():
    options = _parse_command_arguments()
    print(flowerpass(options.passwd, options.key))


if __name__ == '__main__':
    main()
