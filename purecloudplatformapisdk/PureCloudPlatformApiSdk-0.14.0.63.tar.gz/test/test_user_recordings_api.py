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
from swagger_client.apis.user_recordings_api import UserRecordingsApi


class TestUserRecordingsApi(unittest.TestCase):
    """ UserRecordingsApi unit test stubs """

    def setUp(self):
        self.api = swagger_client.apis.user_recordings_api.UserRecordingsApi()

    def tearDown(self):
        pass

    def test_delete_recording_id(self):
        """
        Test case for delete_recording_id

        Delete a user recording.
        """
        pass

    def test_get_recording_id(self):
        """
        Test case for get_recording_id

        Get a user recording.
        """
        pass

    def test_get_recording_id_media(self):
        """
        Test case for get_recording_id_media

        Download a user recording.
        """
        pass

    def test_get_summary(self):
        """
        Test case for get_summary

        Get user recording summary
        """
        pass

    def test_get_userrecordings(self):
        """
        Test case for get_userrecordings

        Get a list of user recordings.
        """
        pass

    def test_put_recording_id(self):
        """
        Test case for put_recording_id

        Update a user recording.
        """
        pass


if __name__ == '__main__':
    unittest.main()