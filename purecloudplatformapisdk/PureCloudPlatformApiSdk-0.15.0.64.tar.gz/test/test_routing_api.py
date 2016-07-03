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
from swagger_client.apis.routing_api import RoutingApi


class TestRoutingApi(unittest.TestCase):
    """ RoutingApi unit test stubs """

    def setUp(self):
        self.api = swagger_client.apis.routing_api.RoutingApi()

    def tearDown(self):
        pass

    def test_delete_email_domains_domain_id(self):
        """
        Test case for delete_email_domains_domain_id

        Delete a domain
        """
        pass

    def test_delete_email_domains_domainname_routes_route_id(self):
        """
        Test case for delete_email_domains_domainname_routes_route_id

        Delete a route
        """
        pass

    def test_delete_queues_queue_id(self):
        """
        Test case for delete_queues_queue_id

        Delete a queue
        """
        pass

    def test_delete_queues_queue_id_users_member_id(self):
        """
        Test case for delete_queues_queue_id_users_member_id

        Delete queue member
        """
        pass

    def test_delete_queues_queue_id_wrapupcodes_code_id(self):
        """
        Test case for delete_queues_queue_id_wrapupcodes_code_id

        Delete a wrap-up code from a queue
        """
        pass

    def test_delete_skills_skill_id(self):
        """
        Test case for delete_skills_skill_id

        Delete Routing Skill
        """
        pass

    def test_delete_user_id_routingskills_skill_id(self):
        """
        Test case for delete_user_id_routingskills_skill_id

        Remove routing skill from user
        """
        pass

    def test_delete_utilization(self):
        """
        Test case for delete_utilization

        Delete utilization settings and revert to system defaults.
        """
        pass

    def test_delete_wrapupcodes_code_id(self):
        """
        Test case for delete_wrapupcodes_code_id

        Delete wrap-up code
        """
        pass

    def test_get_email_domains(self):
        """
        Test case for get_email_domains

        Get domains
        """
        pass

    def test_get_email_domains_domainname_routes(self):
        """
        Test case for get_email_domains_domainname_routes

        Get routes
        """
        pass

    def test_get_email_domains_domainname_routes_route_id(self):
        """
        Test case for get_email_domains_domainname_routes_route_id

        Get a route
        """
        pass

    def test_get_email_setup(self):
        """
        Test case for get_email_setup

        Get email setup
        """
        pass

    def test_get_queues(self):
        """
        Test case for get_queues

        Get list of queues.
        """
        pass

    def test_get_queues_queue_id(self):
        """
        Test case for get_queues_queue_id

        Get details about this queue.
        """
        pass

    def test_get_queues_queue_id_estimatedwaittime(self):
        """
        Test case for get_queues_queue_id_estimatedwaittime

        Get Estimated Wait Time
        """
        pass

    def test_get_queues_queue_id_users(self):
        """
        Test case for get_queues_queue_id_users

        Get the members of this queue
        """
        pass

    def test_get_queues_queue_id_wrapupcodes(self):
        """
        Test case for get_queues_queue_id_wrapupcodes

        Get the wrap-up codes for a queue
        """
        pass

    def test_get_skills(self):
        """
        Test case for get_skills

        Get the list of routing skills.
        """
        pass

    def test_get_skills_skill_id(self):
        """
        Test case for get_skills_skill_id

        Get Routing Skill
        """
        pass

    def test_get_user_id_routingskills(self):
        """
        Test case for get_user_id_routingskills

        List routing skills for user
        """
        pass

    def test_get_utilization(self):
        """
        Test case for get_utilization

        Get the utilization settings.
        """
        pass

    def test_get_wrapupcodes(self):
        """
        Test case for get_wrapupcodes

        Get list of wrapup codes.
        """
        pass

    def test_get_wrapupcodes_code_id(self):
        """
        Test case for get_wrapupcodes_code_id

        Get details about this wrap-up code.
        """
        pass

    def test_patch_queues_queue_id_users(self):
        """
        Test case for patch_queues_queue_id_users

        Join or unjoin a set of users for a queue
        """
        pass

    def test_patch_queues_queue_id_users_member_id(self):
        """
        Test case for patch_queues_queue_id_users_member_id

        Update the ring number of joined status for a User in a Queue
        """
        pass

    def test_post_email_domains(self):
        """
        Test case for post_email_domains

        Create a domain
        """
        pass

    def test_post_email_domains_domainname_routes(self):
        """
        Test case for post_email_domains_domainname_routes

        Create a route
        """
        pass

    def test_post_queues(self):
        """
        Test case for post_queues

        Create queue
        """
        pass

    def test_post_queues_observations_query(self):
        """
        Test case for post_queues_observations_query

        Query for queue observations
        """
        pass

    def test_post_queues_queue_id_users(self):
        """
        Test case for post_queues_queue_id_users

        Bulk add or delete up to 100 queue members
        """
        pass

    def test_post_queues_queue_id_wrapupcodes(self):
        """
        Test case for post_queues_queue_id_wrapupcodes

        Add up to 100 wrap-up codes to a queue
        """
        pass

    def test_post_skills(self):
        """
        Test case for post_skills

        Create Skill
        """
        pass

    def test_post_user_id_routingskills(self):
        """
        Test case for post_user_id_routingskills

        Add routing skill to user
        """
        pass

    def test_post_wrapupcodes(self):
        """
        Test case for post_wrapupcodes

        Create a wrap-up code
        """
        pass

    def test_put_email_domains_domainname_routes_route_id(self):
        """
        Test case for put_email_domains_domainname_routes_route_id

        Update a route
        """
        pass

    def test_put_queues_queue_id(self):
        """
        Test case for put_queues_queue_id

        Update a queue
        """
        pass

    def test_put_user_id_routingskills_skill_id(self):
        """
        Test case for put_user_id_routingskills_skill_id

        Update routing skill proficiency or state.
        """
        pass

    def test_put_utilization(self):
        """
        Test case for put_utilization

        Update the utilization settings.
        """
        pass

    def test_put_wrapupcodes_code_id(self):
        """
        Test case for put_wrapupcodes_code_id

        Update wrap-up code
        """
        pass


if __name__ == '__main__':
    unittest.main()