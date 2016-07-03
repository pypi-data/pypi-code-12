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
from swagger_client.apis.greetings_api import GreetingsApi


class TestGreetingsApi(unittest.TestCase):
    """ GreetingsApi unit test stubs """

    def setUp(self):
        self.api = swagger_client.apis.greetings_api.GreetingsApi()

    def tearDown(self):
        pass

    def test_delete_greeting_id(self):
        """
        Test case for delete_greeting_id

        Deletes a Greeting with the given GreetingId
        """
        pass

    def test_get_defaults(self):
        """
        Test case for get_defaults

        Get an Organization's DefaultGreetingList
        """
        pass

    def test_get_greeting_id(self):
        """
        Test case for get_greeting_id

        Get a Greeting with the given GreetingId
        """
        pass

    def test_get_greeting_id_media(self):
        """
        Test case for get_greeting_id_media

        Get media playback URI for this greeting
        """
        pass

    def test_get_greetings(self):
        """
        Test case for get_greetings

        Gets an Organization's Greetings
        """
        pass

    def test_get_user_id_greetings(self):
        """
        Test case for get_user_id_greetings

        Get a list of the User's Greetings
        """
        pass

    def test_get_user_id_greetings_defaults(self):
        """
        Test case for get_user_id_greetings_defaults

        Grabs the list of Default Greetings given a User's ID
        """
        pass

    def test_post_greetings(self):
        """
        Test case for post_greetings

        Create a Greeting for an Organization
        """
        pass

    def test_post_user_id_greetings(self):
        """
        Test case for post_user_id_greetings

        Creates a Greeting for a User
        """
        pass

    def test_put_defaults(self):
        """
        Test case for put_defaults

        Update an Organization's DefaultGreetingList
        """
        pass

    def test_put_greeting_id(self):
        """
        Test case for put_greeting_id

        Updates the Greeting with the given GreetingId
        """
        pass

    def test_put_user_id_greetings_defaults(self):
        """
        Test case for put_user_id_greetings_defaults

        Updates the DefaultGreetingList of the specified User
        """
        pass


if __name__ == '__main__':
    unittest.main()