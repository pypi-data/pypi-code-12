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
from swagger_client.apis.analytics_api import AnalyticsApi


class TestAnalyticsApi(unittest.TestCase):
    """ AnalyticsApi unit test stubs """

    def setUp(self):
        self.api = swagger_client.apis.analytics_api.AnalyticsApi()

    def tearDown(self):
        pass

    def test_delete_reporting_schedules_schedule_id(self):
        """
        Test case for delete_reporting_schedules_schedule_id

        Delete a scheduled report job.
        """
        pass

    def test_get_conversations_conversation_id_details(self):
        """
        Test case for get_conversations_conversation_id_details

        Get a conversation by id
        """
        pass

    def test_get_reporting_metadata(self):
        """
        Test case for get_reporting_metadata

        Get list of reporting metadata.
        """
        pass

    def test_get_reporting_report_id_metadata(self):
        """
        Test case for get_reporting_report_id_metadata

        Get a reporting metadata.
        """
        pass

    def test_get_reporting_reportformats(self):
        """
        Test case for get_reporting_reportformats

        Get a list of report formats
        """
        pass

    def test_get_reporting_schedules(self):
        """
        Test case for get_reporting_schedules

        Get a list of scheduled report jobs
        """
        pass

    def test_get_reporting_schedules_schedule_id(self):
        """
        Test case for get_reporting_schedules_schedule_id

        Get a scheduled report job.
        """
        pass

    def test_get_reporting_schedules_schedule_id_history(self):
        """
        Test case for get_reporting_schedules_schedule_id_history

        Get list of completed scheduled report jobs.
        """
        pass

    def test_get_reporting_schedules_schedule_id_history_latest(self):
        """
        Test case for get_reporting_schedules_schedule_id_history_latest

        Get most recently completed scheduled report job.
        """
        pass

    def test_get_reporting_schedules_schedule_id_history_run_id(self):
        """
        Test case for get_reporting_schedules_schedule_id_history_run_id

        A completed scheduled report job
        """
        pass

    def test_get_reporting_timeperiods(self):
        """
        Test case for get_reporting_timeperiods

        Get a list of report time periods.
        """
        pass

    def test_post_conversations_aggregates_query(self):
        """
        Test case for post_conversations_aggregates_query

        Query for conversation aggregates
        """
        pass

    def test_post_conversations_conversation_id_details_properties(self):
        """
        Test case for post_conversations_conversation_id_details_properties

        Index conversation properties
        """
        pass

    def test_post_conversations_details_query(self):
        """
        Test case for post_conversations_details_query

        Query for conversation details
        """
        pass

    def test_post_evaluations_aggregates_query(self):
        """
        Test case for post_evaluations_aggregates_query

        Query for evaluation aggregates
        """
        pass

    def test_post_queues_observations_query(self):
        """
        Test case for post_queues_observations_query

        Query for queue observations
        """
        pass

    def test_post_reporting_schedules(self):
        """
        Test case for post_reporting_schedules

        Create a scheduled report job
        """
        pass

    def test_post_reporting_schedules_schedule_id_runreport(self):
        """
        Test case for post_reporting_schedules_schedule_id_runreport

        Place a scheduled report immediately into the reporting queue
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

    def test_put_reporting_schedules_schedule_id(self):
        """
        Test case for put_reporting_schedules_schedule_id

        Update a scheduled report job.
        """
        pass


if __name__ == '__main__':
    unittest.main()