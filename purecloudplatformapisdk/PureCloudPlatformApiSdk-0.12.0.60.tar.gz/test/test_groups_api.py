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
from swagger_client.apis.groups_api import GroupsApi


class TestGroupsApi(unittest.TestCase):
    """ GroupsApi unit test stubs """

    def setUp(self):
        self.api = swagger_client.apis.groups_api.GroupsApi()

    def tearDown(self):
        pass

    def test_delete_group_id_members(self):
        """
        Test case for delete_group_id_members

        Remove members
        """
        pass

    def test_get_group_id(self):
        """
        Test case for get_group_id

        Get group
        """
        pass

    def test_get_group_id_members(self):
        """
        Test case for get_group_id_members

        Get group members
        """
        pass

    def test_get_groups(self):
        """
        Test case for get_groups

        Get a group list
        """
        pass

    def test_get_search(self):
        """
        Test case for get_search

        Search using q64
        """
        pass

    def test_post_group_id_members(self):
        """
        Test case for post_group_id_members

        Add members
        """
        pass

    def test_post_groups(self):
        """
        Test case for post_groups

        Create a group
        """
        pass

    def test_post_search(self):
        """
        Test case for post_search

        Search
        """
        pass


if __name__ == '__main__':
    unittest.main()