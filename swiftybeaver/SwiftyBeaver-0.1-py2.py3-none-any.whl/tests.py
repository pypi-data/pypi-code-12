# -*- coding: utf-8 -*-

# The MIT License (MIT)
# https://opensource.org/licenses/MIT
#
# Copyright © 2016 Sebastian Kreutzberger, Steffen Ryll. Some Rights Reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

'''Automated test cases for SwiftyBeaver Platform.'''


from logging import LogRecord
from unittest import TestCase

from swiftybeaver import SwiftyBeaverAPI, SwiftyBeaverHandler

HTTP_BIN = 'http://httpbin.org/{}'
MOCK_CREDENTIALS = 'app_id', 'app_secret', '0123456789abcdef'
MOCK_ENTRIES = [
    {'level': 1},
    {'level': 2},
    {'level': 3}
]


class TestSwiftyBeaverAPI(TestCase):

    def setUp(self):
        self.api = SwiftyBeaverAPI(*MOCK_CREDENTIALS)
        self.api.API_URL = HTTP_BIN

    def test_generate_encryption_iv(self):
        iv = self.api._generate_encryption_iv()

        self.assertEqual(len(iv), self.api.BLOCK_SIZE)

    def test_pad_string(self):
        padded_string = self.api._pad_string('0123456789')

        self.assertEqual(padded_string, '0123456789\x06\x06\x06\x06\x06\x06')

    def test_encrypt_payload(self):
        string_encrypted = self.api.encrypt_payload('{"test": 42}')
        json_encrypted = self.api.encrypt_payload({'test': 42})

        self.assertTrue(string_encrypted)
        self.assertTrue(json_encrypted)

    def test_post(self):
        def callback(response):
            self.assertEqual(response.status_code, 200)

        self.api.post('post', callback=callback).result()

    def test_post_entries(self):
        def callback(response):
            self.assertEqual(response.status_code, 404)

        self.api.post_entries([{'key': 'value'}], {'key': 'value'}, callback=callback).result()


class TestSwiftyBeaverHandler(TestCase):

    def setUp(self):
        self.handler = SwiftyBeaverHandler(*MOCK_CREDENTIALS)
        self.handler.api.API_URL = HTTP_BIN

    def test_emit(self):
        record = LogRecord('Test', 1, 'test.py', 42, 'Hello world!', [], None)

        self.handler.entries = []
        self.handler.emit(record)

        entry = self.handler.entries[0]

        self.assertEqual(len(entry.keys()), 7)
        self.assertEqual(entry['fileName'], 'test.py')
        self.assertEqual(entry['level'], 0)
        self.assertEqual(entry['line'], 42)
        self.assertEqual(entry['message'], 'Hello world!')
        self.assertTrue(entry['thread'].startswith('MainThread'))

    def test_logging_points(self):
        self.handler.entries = MOCK_ENTRIES

        self.assertEqual(self.handler.logging_points, 1 + 5 + 8)

    def test_send_log_entries(self):
        self.handler.entries = MOCK_ENTRIES
        self.handler.send_log_entries().result()
