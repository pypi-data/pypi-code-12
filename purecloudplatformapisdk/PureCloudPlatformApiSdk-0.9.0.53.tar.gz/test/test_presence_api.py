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
from swagger_client.apis.presence_api import PresenceApi


class TestPresenceApi(unittest.TestCase):
    """ PresenceApi unit test stubs """

    def setUp(self):
        self.api = swagger_client.apis.presence_api.PresenceApi()

    def tearDown(self):
        pass

    def test_delete_presence_id(self):
        """
        Test case for delete_presence_id

        Delete a Presence Definition
        """
        pass

    def test_get_presence_id(self):
        """
        Test case for get_presence_id

        Get a Presence Definition
        """
        pass

    def test_get_presencedefinitions(self):
        """
        Test case for get_presencedefinitions

        Get an Organization's list of Presence Definitions
        """
        pass

    def test_get_systempresences(self):
        """
        Test case for get_systempresences

        Get the list of SystemPresences
        """
        pass

    def test_get_user_id_presences_source_id(self):
        """
        Test case for get_user_id_presences_source_id

        Get a user's Presence
        """
        pass

    def test_patch_user_id_presences_source_id(self):
        """
        Test case for patch_user_id_presences_source_id

        Patch a user's Presence
        """
        pass

    def test_post_presencedefinitions(self):
        """
        Test case for post_presencedefinitions

        Create a Presence Definition
        """
        pass

    def test_put_presence_id(self):
        """
        Test case for put_presence_id

        Update a Presence Definition
        """
        pass


if __name__ == '__main__':
    unittest.main()