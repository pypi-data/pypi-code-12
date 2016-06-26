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
from swagger_client.apis.attributes_api import AttributesApi


class TestAttributesApi(unittest.TestCase):
    """ AttributesApi unit test stubs """

    def setUp(self):
        self.api = swagger_client.apis.attributes_api.AttributesApi()

    def tearDown(self):
        pass

    def test_delete_attribute_id(self):
        """
        Test case for delete_attribute_id

        Delete an existing Attribute.
        """
        pass

    def test_get_attribute_id(self):
        """
        Test case for get_attribute_id

        Get details about an existing attribute.
        """
        pass

    def test_get_attributes(self):
        """
        Test case for get_attributes

        Gets a list of existing attributes.
        """
        pass

    def test_post_attributes(self):
        """
        Test case for post_attributes

        Create an attribute.
        """
        pass

    def test_post_query(self):
        """
        Test case for post_query

        Query attributes
        """
        pass

    def test_put_attribute_id(self):
        """
        Test case for put_attribute_id

        Update an existing attribute.
        """
        pass


if __name__ == '__main__':
    unittest.main()