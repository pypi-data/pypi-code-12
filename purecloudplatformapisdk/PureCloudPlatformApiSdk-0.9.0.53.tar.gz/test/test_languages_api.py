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
from swagger_client.apis.languages_api import LanguagesApi


class TestLanguagesApi(unittest.TestCase):
    """ LanguagesApi unit test stubs """

    def setUp(self):
        self.api = swagger_client.apis.languages_api.LanguagesApi()

    def tearDown(self):
        pass

    def test_delete_language_id(self):
        """
        Test case for delete_language_id

        Delete Language
        """
        pass

    def test_get_language_id(self):
        """
        Test case for get_language_id

        Get language
        """
        pass

    def test_get_languages(self):
        """
        Test case for get_languages

        Get the list of supported languages.
        """
        pass

    def test_post_languages(self):
        """
        Test case for post_languages

        Create Language
        """
        pass

    def test_put_language_id(self):
        """
        Test case for put_language_id

        Update Language
        """
        pass


if __name__ == '__main__':
    unittest.main()