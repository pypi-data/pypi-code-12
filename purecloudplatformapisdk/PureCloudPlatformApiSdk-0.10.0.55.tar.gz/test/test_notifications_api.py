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
from swagger_client.apis.notifications_api import NotificationsApi


class TestNotificationsApi(unittest.TestCase):
    """ NotificationsApi unit test stubs """

    def setUp(self):
        self.api = swagger_client.apis.notifications_api.NotificationsApi()

    def tearDown(self):
        pass

    def test_delete_channels_channel_id_subscriptions(self):
        """
        Test case for delete_channels_channel_id_subscriptions

        Remove all subscriptions
        """
        pass

    def test_get_availabletopics(self):
        """
        Test case for get_availabletopics

        Get available notification topics.
        """
        pass

    def test_get_channels(self):
        """
        Test case for get_channels

        The list of existing channels
        """
        pass

    def test_get_channels_channel_id_subscriptions(self):
        """
        Test case for get_channels_channel_id_subscriptions

        The list of all subscriptions for this channel
        """
        pass

    def test_post_channels(self):
        """
        Test case for post_channels

        Create a new channel
        """
        pass

    def test_post_channels_channel_id_subscriptions(self):
        """
        Test case for post_channels_channel_id_subscriptions

        Add a list of subscriptions to the existing list of subscriptions
        """
        pass

    def test_put_channels_channel_id_subscriptions(self):
        """
        Test case for put_channels_channel_id_subscriptions

        Replace the current list of subscriptions with a new list.
        """
        pass


if __name__ == '__main__':
    unittest.main()