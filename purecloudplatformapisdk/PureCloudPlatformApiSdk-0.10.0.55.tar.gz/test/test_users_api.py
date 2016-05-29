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
from swagger_client.apis.users_api import UsersApi


class TestUsersApi(unittest.TestCase):
    """ UsersApi unit test stubs """

    def setUp(self):
        self.api = swagger_client.apis.users_api.UsersApi()

    def tearDown(self):
        pass

    def test_delete_user_id(self):
        """
        Test case for delete_user_id

        Delete user
        """
        pass

    def test_delete_user_id_roles(self):
        """
        Test case for delete_user_id_roles

        Removes all the roles from the user.
        """
        pass

    def test_delete_user_id_routingskills_skill_id(self):
        """
        Test case for delete_user_id_routingskills_skill_id

        Remove routing skill from user
        """
        pass

    def test_delete_user_id_station_associatedstation(self):
        """
        Test case for delete_user_id_station_associatedstation

        Clear associated station
        """
        pass

    def test_delete_user_id_station_defaultstation(self):
        """
        Test case for delete_user_id_station_defaultstation

        Clear default station
        """
        pass

    def test_get_me(self):
        """
        Test case for get_me

        Get user.
        """
        pass

    def test_get_search(self):
        """
        Test case for get_search

        Search using q64
        """
        pass

    def test_get_user_id(self):
        """
        Test case for get_user_id

        Get user
        """
        pass

    def test_get_user_id_callforwarding(self):
        """
        Test case for get_user_id_callforwarding

        Get a user's CallForwarding
        """
        pass

    def test_get_user_id_geolocations_client_id(self):
        """
        Test case for get_user_id_geolocations_client_id

        Get a user's Geolocation
        """
        pass

    def test_get_user_id_outofoffice(self):
        """
        Test case for get_user_id_outofoffice

        Get a OutOfOffice
        """
        pass

    def test_get_user_id_queues(self):
        """
        Test case for get_user_id_queues

        Get queues for user
        """
        pass

    def test_get_user_id_roles(self):
        """
        Test case for get_user_id_roles

        Returns a listing of roles and permissions for a user.
        """
        pass

    def test_get_user_id_routingskills(self):
        """
        Test case for get_user_id_routingskills

        List routing skills for user
        """
        pass

    def test_get_user_id_routingstatus(self):
        """
        Test case for get_user_id_routingstatus

        Fetch the routing status of a user
        """
        pass

    def test_get_user_id_station(self):
        """
        Test case for get_user_id_station

        Get station information for user
        """
        pass

    def test_get_users(self):
        """
        Test case for get_users

        Get the list of available users.
        """
        pass

    def test_patch_user_id(self):
        """
        Test case for patch_user_id

        Update user
        """
        pass

    def test_patch_user_id_callforwarding(self):
        """
        Test case for patch_user_id_callforwarding

        Patch a user's CallForwarding
        """
        pass

    def test_patch_user_id_geolocations_client_id(self):
        """
        Test case for patch_user_id_geolocations_client_id

        Patch a user's Geolocation
        """
        pass

    def test_patch_user_id_queues(self):
        """
        Test case for patch_user_id_queues

        Join or unjoin a set of queues for a user
        """
        pass

    def test_patch_user_id_queues_queue_id(self):
        """
        Test case for patch_user_id_queues_queue_id

        Join or unjoin a queue for a user
        """
        pass

    def test_post_search(self):
        """
        Test case for post_search

        Search
        """
        pass

    def test_post_user_id_routingskills(self):
        """
        Test case for post_user_id_routingskills

        Add routing skill to user
        """
        pass

    def test_post_users(self):
        """
        Test case for post_users

        Create user
        """
        pass

    def test_post_users_aggregates_query(self):
        """
        Test case for post_users_aggregates_query

        Query for user aggregates
        """
        pass

    def test_post_users_observations_query(self):
        """
        Test case for post_users_observations_query

        Query for user observations
        """
        pass

    def test_put_user_id_callforwarding(self):
        """
        Test case for put_user_id_callforwarding

        Update a user's CallForwarding
        """
        pass

    def test_put_user_id_outofoffice(self):
        """
        Test case for put_user_id_outofoffice

        Update an OutOfOffice
        """
        pass

    def test_put_user_id_roles(self):
        """
        Test case for put_user_id_roles

        Sets the user's roles
        """
        pass

    def test_put_user_id_routingskills_skill_id(self):
        """
        Test case for put_user_id_routingskills_skill_id

        Update routing skill proficiency or state.
        """
        pass

    def test_put_user_id_routingstatus(self):
        """
        Test case for put_user_id_routingstatus

        Update the routing status of a user
        """
        pass

    def test_put_user_id_station_associatedstation_station_id(self):
        """
        Test case for put_user_id_station_associatedstation_station_id

        Set associated station
        """
        pass

    def test_put_user_id_station_defaultstation_station_id(self):
        """
        Test case for put_user_id_station_defaultstation_station_id

        Set default station
        """
        pass


if __name__ == '__main__':
    unittest.main()