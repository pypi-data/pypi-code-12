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
from swagger_client.apis.quality_api import QualityApi


class TestQualityApi(unittest.TestCase):
    """ QualityApi unit test stubs """

    def setUp(self):
        self.api = swagger_client.apis.quality_api.QualityApi()

    def tearDown(self):
        pass

    def test_delete_calibrations_calibration_id(self):
        """
        Test case for delete_calibrations_calibration_id

        Delete a calibration by id.
        """
        pass

    def test_delete_conversations_conversation_id_evaluations_evaluation_id(self):
        """
        Test case for delete_conversations_conversation_id_evaluations_evaluation_id

        Delete an evaluation
        """
        pass

    def test_delete_forms_form_id(self):
        """
        Test case for delete_forms_form_id

        Delete an evaluation form.
        """
        pass

    def test_delete_keywordsets(self):
        """
        Test case for delete_keywordsets

        Delete keyword sets
        """
        pass

    def test_delete_keywordsets_keywordset_id(self):
        """
        Test case for delete_keywordsets_keywordset_id

        Delete a keywordSet by id.
        """
        pass

    def test_get_agents_activity(self):
        """
        Test case for get_agents_activity

        Gets a list of Agent Activities
        """
        pass

    def test_get_calibrations(self):
        """
        Test case for get_calibrations

        Get the list of calibrations
        """
        pass

    def test_get_calibrations_calibration_id(self):
        """
        Test case for get_calibrations_calibration_id

        Get a calibration by id.
        """
        pass

    def test_get_conversations_conversation_id_audits(self):
        """
        Test case for get_conversations_conversation_id_audits

        Get audits for conversation or recording
        """
        pass

    def test_get_conversations_conversation_id_evaluations_evaluation_id(self):
        """
        Test case for get_conversations_conversation_id_evaluations_evaluation_id

        Get an evaluation
        """
        pass

    def test_get_evaluations_query(self):
        """
        Test case for get_evaluations_query

        Queries Evaluations and returns a paged list
        """
        pass

    def test_get_evaluators_activity(self):
        """
        Test case for get_evaluators_activity

        Get an evaluator activity
        """
        pass

    def test_get_forms(self):
        """
        Test case for get_forms

        Get the list of evaluation forms
        """
        pass

    def test_get_forms_form_id(self):
        """
        Test case for get_forms_form_id

        Get an evaluation form
        """
        pass

    def test_get_forms_form_id_versions(self):
        """
        Test case for get_forms_form_id_versions

        Gets all the revisions for a specific evaluation.
        """
        pass

    def test_get_keywordsets(self):
        """
        Test case for get_keywordsets

        Get the list of keyword sets
        """
        pass

    def test_get_keywordsets_keywordset_id(self):
        """
        Test case for get_keywordsets_keywordset_id

        Get a keywordSet by id.
        """
        pass

    def test_get_publishedforms(self):
        """
        Test case for get_publishedforms

        Get the published evaluation forms.
        """
        pass

    def test_get_publishedforms_form_id(self):
        """
        Test case for get_publishedforms_form_id

        Get the published evaluation forms.
        """
        pass

    def test_post_calibrations(self):
        """
        Test case for post_calibrations

        Create a calibration
        """
        pass

    def test_post_conversations_conversation_id_evaluations(self):
        """
        Test case for post_conversations_conversation_id_evaluations

        Create an evaluation
        """
        pass

    def test_post_evaluations_aggregates_query(self):
        """
        Test case for post_evaluations_aggregates_query

        Query for evaluation aggregates
        """
        pass

    def test_post_evaluations_scoring(self):
        """
        Test case for post_evaluations_scoring

        Score evaluation
        """
        pass

    def test_post_forms(self):
        """
        Test case for post_forms

        Create an evaluation form.
        """
        pass

    def test_post_keywordsets(self):
        """
        Test case for post_keywordsets

        Create a Keyword Set
        """
        pass

    def test_post_publishedforms(self):
        """
        Test case for post_publishedforms

        Publish an evaluation form.
        """
        pass

    def test_put_calibrations_calibration_id(self):
        """
        Test case for put_calibrations_calibration_id

        Update a calibration to the specified calibration via PUT.  Editable fields include: evaluators, expertEvaluator, and scoringIndex
        """
        pass

    def test_put_conversations_conversation_id_evaluations_evaluation_id(self):
        """
        Test case for put_conversations_conversation_id_evaluations_evaluation_id

        Update an evaluation
        """
        pass

    def test_put_forms_form_id(self):
        """
        Test case for put_forms_form_id

        Update an evaluation form.
        """
        pass

    def test_put_keywordsets_keywordset_id(self):
        """
        Test case for put_keywordsets_keywordset_id

        Update a keywordSet to the specified keywordSet via PUT.
        """
        pass


if __name__ == '__main__':
    unittest.main()