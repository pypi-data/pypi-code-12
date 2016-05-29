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
from swagger_client.apis.o_auth_api import OAuthApi


class TestOAuthApi(unittest.TestCase):
    """ OAuthApi unit test stubs """

    def setUp(self):
        self.api = swagger_client.apis.o_auth_api.OAuthApi()

    def tearDown(self):
        pass

    def test_delete_clients_client_id(self):
        """
        Test case for delete_clients_client_id

        Delete OAuth Client
        """
        pass

    def test_get_clients(self):
        """
        Test case for get_clients

        The list of OAuth clients
        """
        pass

    def test_get_clients_client_id(self):
        """
        Test case for get_clients_client_id

        Get OAuth Client
        """
        pass

    def test_post_clients(self):
        """
        Test case for post_clients

        Create OAuth client
        """
        pass

    def test_post_clients_client_id_secret(self):
        """
        Test case for post_clients_client_id_secret

        Regenerate Client Secret
        """
        pass

    def test_put_clients_client_id(self):
        """
        Test case for put_clients_client_id

        Update OAuth Client
        """
        pass


if __name__ == '__main__':
    unittest.main()