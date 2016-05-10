#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_msg91
----------------------------------

Tests for `msg91` module.
"""

import unittest

from msg91 import MSG91Client


class TestMsg91(unittest.TestCase):

    def setUp(self):
        api_key = ''  # todo: add api key for testing sms
        app_key = ''  # todo: add app key for testing otp
        self.client = MSG91Client(api_key=api_key, app_key=app_key)

    def tearDown(self):
        pass

    def test_send_sms(self):
        #self.client.send_sms('Test SMS', '9971636025')
        pass

    def test_verify_otp(self):
        #self.client.check_otp_status('9971636025', 'adbkhDGvad72t8HJDVd396HD')
        pass

    def test_send_otp(self):
        self.client.generate_otp('9971XXXXXX')


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())