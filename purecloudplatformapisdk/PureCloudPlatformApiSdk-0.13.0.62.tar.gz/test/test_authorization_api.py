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
from swagger_client.apis.authorization_api import AuthorizationApi


class TestAuthorizationApi(unittest.TestCase):
    """ AuthorizationApi unit test stubs """

    def setUp(self):
        self.api = swagger_client.apis.authorization_api.AuthorizationApi()

    def tearDown(self):
        pass

    def test_delete_roles_role_id(self):
        """
        Test case for delete_roles_role_id

        Delete an organization role.
        """
        pass

    def test_delete_user_id_roles(self):
        """
        Test case for delete_user_id_roles

        Removes all the roles from the user.
        """
        pass

    def test_get_permissions(self):
        """
        Test case for get_permissions

        Get all permissions.
        """
        pass

    def test_get_products(self):
        """
        Test case for get_products

        Get the list of enabled products
        """
        pass

    def test_get_roles(self):
        """
        Test case for get_roles

        Retrieve a list of all roles defined for the organization
        """
        pass

    def test_get_roles_leftrole_id_comparedefault_rightrole_id(self):
        """
        Test case for get_roles_leftrole_id_comparedefault_rightrole_id

        Get an org role to default role comparison comparison
        """
        pass

    def test_get_roles_role_id(self):
        """
        Test case for get_roles_role_id

        Get a single organization role.
        """
        pass

    def test_get_user_id_roles(self):
        """
        Test case for get_user_id_roles

        Returns a listing of roles and permissions for a user.
        """
        pass

    def test_patch_roles_role_id(self):
        """
        Test case for patch_roles_role_id

        Patch Organization Role for needsUpdate Field
        """
        pass

    def test_post_roles(self):
        """
        Test case for post_roles

        Create an organization role.
        """
        pass

    def test_post_roles_default(self):
        """
        Test case for post_roles_default

        Restores all default roles
        """
        pass

    def test_post_roles_leftrole_id_comparedefault_rightrole_id(self):
        """
        Test case for post_roles_leftrole_id_comparedefault_rightrole_id

         Get an unsaved org role to default role comparison
        """
        pass

    def test_put_roles_default(self):
        """
        Test case for put_roles_default

        Restore specified default roles
        """
        pass

    def test_put_roles_role_id(self):
        """
        Test case for put_roles_role_id

        Update an organization role.
        """
        pass

    def test_put_roles_role_id_users_add(self):
        """
        Test case for put_roles_role_id_users_add

        Sets the users for the role
        """
        pass

    def test_put_roles_role_id_users_remove(self):
        """
        Test case for put_roles_role_id_users_remove

        Removes the users from the role
        """
        pass

    def test_put_user_id_roles(self):
        """
        Test case for put_user_id_roles

        Sets the user's roles
        """
        pass


if __name__ == '__main__':
    unittest.main()