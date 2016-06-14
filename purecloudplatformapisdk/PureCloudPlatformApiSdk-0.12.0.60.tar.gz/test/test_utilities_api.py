# coding: utf-8

"""
Copyright 2016 SmartBear Software

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

   ref: https://github.com/swagger-api/swagger-codegen
"""

from __future__ import absolute_import

import os
import sys
import unittest

import swagger_client
from swagger_client.rest import ApiException
from swagger_client.apis.utilities_api import UtilitiesApi


class TestUtilitiesApi(unittest.TestCase):
    """ UtilitiesApi unit test stubs """

    def setUp(self):
        self.api = swagger_client.apis.utilities_api.UtilitiesApi()

    def tearDown(self):
        pass

    def test_get_date(self):
        """
        Test case for get_date

        Get the current system date/time
        """
        pass

    def test_get_timezones(self):
        """
        Test case for get_timezones

        Get time zones list
        """
        pass

    def test_post_details(self):
        """
        Test case for post_details

        Returns the information about an X509 PEM encoded certificate or certificate chain.
        """
        pass


if __name__ == '__main__':
    unittest.main()