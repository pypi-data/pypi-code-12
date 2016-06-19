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
from swagger_client.apis.identity_provider_api import IdentityProviderApi


class TestIdentityProviderApi(unittest.TestCase):
    """ IdentityProviderApi unit test stubs """

    def setUp(self):
        self.api = swagger_client.apis.identity_provider_api.IdentityProviderApi()

    def tearDown(self):
        pass

    def test_delete_adfs(self):
        """
        Test case for delete_adfs

        Delete ADFS Identity Provider
        """
        pass

    def test_delete_cic(self):
        """
        Test case for delete_cic

        Delete Customer Interaction Center (CIC) Identity Provider
        """
        pass

    def test_delete_okta(self):
        """
        Test case for delete_okta

        Delete Okta Identity Provider
        """
        pass

    def test_delete_onelogin(self):
        """
        Test case for delete_onelogin

        Delete OneLogin Identity Provider
        """
        pass

    def test_delete_provider_id(self):
        """
        Test case for delete_provider_id

        Delete an identity provider
        """
        pass

    def test_delete_purecloud(self):
        """
        Test case for delete_purecloud

        Delete PureCloud Identity Provider
        """
        pass

    def test_delete_salesforce(self):
        """
        Test case for delete_salesforce

        Delete Salesforce Identity Provider
        """
        pass

    def test_get_adfs(self):
        """
        Test case for get_adfs

        Get ADFS Identity Provider
        """
        pass

    def test_get_cic(self):
        """
        Test case for get_cic

        Get Customer Interaction Center (CIC) Identity Provider
        """
        pass

    def test_get_identityproviders(self):
        """
        Test case for get_identityproviders

        The list of identity providers
        """
        pass

    def test_get_okta(self):
        """
        Test case for get_okta

        Get Okta Identity Provider
        """
        pass

    def test_get_onelogin(self):
        """
        Test case for get_onelogin

        Get OneLogin Identity Provider
        """
        pass

    def test_get_provider_id(self):
        """
        Test case for get_provider_id

        Get an identity provider
        """
        pass

    def test_get_purecloud(self):
        """
        Test case for get_purecloud

        Get PureCloud Identity Provider
        """
        pass

    def test_get_salesforce(self):
        """
        Test case for get_salesforce

        Get Salesforce Identity Provider
        """
        pass

    def test_put_adfs(self):
        """
        Test case for put_adfs

        Update/Create ADFS Identity Provider
        """
        pass

    def test_put_cic(self):
        """
        Test case for put_cic

        Update/Create Customer Interaction Center (CIC) Identity Provider
        """
        pass

    def test_put_okta(self):
        """
        Test case for put_okta

        Update/Create Okta Identity Provider
        """
        pass

    def test_put_onelogin(self):
        """
        Test case for put_onelogin

        Update/Create OneLogin Identity Provider
        """
        pass

    def test_put_provider_id(self):
        """
        Test case for put_provider_id

        Update an identity provider
        """
        pass

    def test_put_purecloud(self):
        """
        Test case for put_purecloud

        Update/Create PureCloud Identity Provider
        """
        pass

    def test_put_salesforce(self):
        """
        Test case for put_salesforce

        Update/Create Salesforce Identity Provider
        """
        pass


if __name__ == '__main__':
    unittest.main()