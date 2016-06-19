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
from swagger_client.apis.response_management_api import ResponseManagementApi


class TestResponseManagementApi(unittest.TestCase):
    """ ResponseManagementApi unit test stubs """

    def setUp(self):
        self.api = swagger_client.apis.response_management_api.ResponseManagementApi()

    def tearDown(self):
        pass

    def test_delete_libraries_library_id(self):
        """
        Test case for delete_libraries_library_id

        Delete an existing response library.
        """
        pass

    def test_delete_responses_response_id(self):
        """
        Test case for delete_responses_response_id

        Delete an existing response.
        """
        pass

    def test_get_libraries(self):
        """
        Test case for get_libraries

        Gets a list of existing response libraries.
        """
        pass

    def test_get_libraries_library_id(self):
        """
        Test case for get_libraries_library_id

        Get details about an existing response library.
        """
        pass

    def test_get_responses(self):
        """
        Test case for get_responses

        Gets a list of existing responses.
        """
        pass

    def test_get_responses_response_id(self):
        """
        Test case for get_responses_response_id

        Get details about an existing response.
        """
        pass

    def test_post_libraries(self):
        """
        Test case for post_libraries

        Create a response library.
        """
        pass

    def test_post_responses(self):
        """
        Test case for post_responses

        Create a response.
        """
        pass

    def test_post_responses_query(self):
        """
        Test case for post_responses_query

        Query responses
        """
        pass

    def test_put_libraries_library_id(self):
        """
        Test case for put_libraries_library_id

        Update an existing response library.
        """
        pass

    def test_put_responses_response_id(self):
        """
        Test case for put_responses_response_id

        Update an existing response.
        """
        pass


if __name__ == '__main__':
    unittest.main()