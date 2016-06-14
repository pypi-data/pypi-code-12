# -*- coding: utf-8 -*-

import unittest

import cos2
from cos2.exceptions import make_exception

import os
import sys
import tempfile

from common import *


is_py2 = (sys.version_info[0] == 2)
is_py3 = (sys.version_info[0] == 3)


class TestUtils(CosTestCase):
    def test_is_ip(self):
        self.assertTrue(cos2.utils.is_ip_or_localhost('1.2.3.4'))
        self.assertTrue(cos2.utils.is_ip_or_localhost('localhost'))

        self.assertTrue(not cos2.utils.is_ip_or_localhost('-1.2.3.4'))
        self.assertTrue(not cos2.utils.is_ip_or_localhost('1.256.1.2'))
        self.assertTrue(not cos2.utils.is_ip_or_localhost('一.二.三.四'))

    def test_is_valid_bucket_name(self):
        self.assertTrue(cos2.is_valid_bucket_name('abc'))
        self.assertTrue(cos2.is_valid_bucket_name('hello-world'))

        self.assertTrue(not cos2.is_valid_bucket_name('HELLO'))
        self.assertTrue(not cos2.is_valid_bucket_name('hello_world'))
        self.assertTrue(not cos2.is_valid_bucket_name('hello-'))
        self.assertTrue(not cos2.is_valid_bucket_name('-hello'))

    def test_compat(self):
        # from unicode
        u = u'中文'

        self.assertEqual(u, cos2.to_unicode(u))
        self.assertEqual(u.encode('utf-8'), cos2.to_bytes(u))

        if is_py2:
            self.assertEqual(u.encode('utf-8'), cos2.to_string(u))

        if is_py3:
            self.assertEqual(u, cos2.to_string(u))

        # from bytes
        b = u.encode('utf-8')

        self.assertEqual(b.decode('utf-8'), cos2.to_unicode(b))
        self.assertEqual(b, cos2.to_bytes(b))

        if is_py2:
            self.assertEqual(b, cos2.to_string(b))

        if is_py3:
            self.assertEqual(b.decode('utf-8'), cos2.to_string(b))

    def test_makedir_p(self):
        tempdir = tempfile.gettempdir()

        dirpath = os.path.join(tempdir, random_string(10))

        cos2.utils.makedir_p(dirpath)
        os.path.isdir(dirpath)

        # recreate same dir should not issue an error
        cos2.utils.makedir_p(dirpath)

    def __fake_response(self, status, error_body):
        key = self.random_key()

        self.bucket.put_object(key, cos2.to_bytes(error_body))
        resp = self.bucket.get_object(key).resp
        resp.status = status

        return resp

    def test_make_exception(self):
        body = 'bad body'
        e = make_exception(self.__fake_response(400, body))
        self.assertTrue(isinstance(e, cos2.exceptions.ServerError))
        self.assertEqual(e.status, 400)
        self.assertEqual(e.body, cos2.to_bytes(body))

        # body = '<Error><Code>NoSuchKey</Code><Message>中文和控制字符&#12;</Message></Error>'
        body = '{"Code": "NoSuchKey","Message": "中文和控制字符#12;"}'

        e = make_exception(self.__fake_response(404, body))
        self.assertTrue(isinstance(e, cos2.exceptions.NoSuchKey))
        self.assertEqual(e.status, 404)
        self.assertEqual(e.code, 'NoSuchKey')


if __name__ == '__main__':
    unittest.main()