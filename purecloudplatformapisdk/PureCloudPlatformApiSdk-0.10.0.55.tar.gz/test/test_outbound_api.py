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
from swagger_client.apis.outbound_api import OutboundApi


class TestOutboundApi(unittest.TestCase):
    """ OutboundApi unit test stubs """

    def setUp(self):
        self.api = swagger_client.apis.outbound_api.OutboundApi()

    def tearDown(self):
        pass

    def test_delete_callabletimesets_callabletimeset_id(self):
        """
        Test case for delete_callabletimesets_callabletimeset_id

        Delete callable time set
        """
        pass

    def test_delete_callanalysisresponsesets_callanalysisset_id(self):
        """
        Test case for delete_callanalysisresponsesets_callanalysisset_id

        Delete a dialer call analysis response set.
        """
        pass

    def test_delete_campaigns_campaign_id(self):
        """
        Test case for delete_campaigns_campaign_id

        Delete a campaign.
        """
        pass

    def test_delete_campaigns_campaign_id_progress(self):
        """
        Test case for delete_campaigns_campaign_id_progress

        Reset campaign progress and recycle the campaign
        """
        pass

    def test_delete_contactlists_contactlist_id(self):
        """
        Test case for delete_contactlists_contactlist_id

        Delete a contact list.
        """
        pass

    def test_delete_contactlists_contactlist_id_contacts_contact_id(self):
        """
        Test case for delete_contactlists_contactlist_id_contacts_contact_id

        Delete a contact.
        """
        pass

    def test_delete_dnclists_dnclist_id(self):
        """
        Test case for delete_dnclists_dnclist_id

        Delete dialer DNC list
        """
        pass

    def test_delete_rulesets_ruleset_id(self):
        """
        Test case for delete_rulesets_ruleset_id

        Delete a Rule set.
        """
        pass

    def test_delete_schedules_campaigns_campaign_id(self):
        """
        Test case for delete_schedules_campaigns_campaign_id

        Delete a dialer campaign schedule.
        """
        pass

    def test_delete_schedules_sequences_sequence_id(self):
        """
        Test case for delete_schedules_sequences_sequence_id

        Delete a dialer sequence schedule.
        """
        pass

    def test_delete_sequences_sequence_id(self):
        """
        Test case for delete_sequences_sequence_id

        Delete a dialer campaign sequence.
        """
        pass

    def test_get_callabletimesets(self):
        """
        Test case for get_callabletimesets

        Query callable time set list
        """
        pass

    def test_get_callabletimesets_callabletimeset_id(self):
        """
        Test case for get_callabletimesets_callabletimeset_id

        Get callable time set
        """
        pass

    def test_get_callanalysisresponsesets(self):
        """
        Test case for get_callanalysisresponsesets

        Query a list of dialer call analysis response sets.
        """
        pass

    def test_get_callanalysisresponsesets_callanalysisset_id(self):
        """
        Test case for get_callanalysisresponsesets_callanalysisset_id

        Get a dialer call analysis response set.
        """
        pass

    def test_get_campaigns(self):
        """
        Test case for get_campaigns

        Query a list of dialer campaigns.
        """
        pass

    def test_get_campaigns_campaign_id(self):
        """
        Test case for get_campaigns_campaign_id

        Get dialer campaign.
        """
        pass

    def test_get_campaigns_campaign_id_diagnostics(self):
        """
        Test case for get_campaigns_campaign_id_diagnostics

        Get campaign diagnostics
        """
        pass

    def test_get_campaigns_campaign_id_progress(self):
        """
        Test case for get_campaigns_campaign_id_progress

        Get campaign progress
        """
        pass

    def test_get_campaigns_campaign_id_stats(self):
        """
        Test case for get_campaigns_campaign_id_stats

        Get statistics about a Dialer Campaign
        """
        pass

    def test_get_contactlists(self):
        """
        Test case for get_contactlists

        Query a list of contact lists.
        """
        pass

    def test_get_contactlists_contactlist_id(self):
        """
        Test case for get_contactlists_contactlist_id

        Get a dialer contact list.
        """
        pass

    def test_get_contactlists_contactlist_id_contacts_contact_id(self):
        """
        Test case for get_contactlists_contactlist_id_contacts_contact_id

        Get dialer contactList.
        """
        pass

    def test_get_contactlists_contactlist_id_export(self):
        """
        Test case for get_contactlists_contactlist_id_export

        Get the URI of a contact list export.
        """
        pass

    def test_get_contactlists_contactlist_id_importstatus(self):
        """
        Test case for get_contactlists_contactlist_id_importstatus

        Get dialer contactList import status.
        """
        pass

    def test_get_dnclists(self):
        """
        Test case for get_dnclists

        Query dialer DNC lists
        """
        pass

    def test_get_dnclists_dnclist_id(self):
        """
        Test case for get_dnclists_dnclist_id

        Get dialer DNC list
        """
        pass

    def test_get_dnclists_dnclist_id_export(self):
        """
        Test case for get_dnclists_dnclist_id_export

        Get the URI of a DNC list export.
        """
        pass

    def test_get_dnclists_dnclist_id_importstatus(self):
        """
        Test case for get_dnclists_dnclist_id_importstatus

        Get dialer dncList import status.
        """
        pass

    def test_get_rulesets(self):
        """
        Test case for get_rulesets

        Query a list of Rule Sets.
        """
        pass

    def test_get_rulesets_ruleset_id(self):
        """
        Test case for get_rulesets_ruleset_id

        Get a Rule Set by ID.
        """
        pass

    def test_get_schedules_campaigns(self):
        """
        Test case for get_schedules_campaigns

        Query for a list of dialer campaign schedules.
        """
        pass

    def test_get_schedules_campaigns_campaign_id(self):
        """
        Test case for get_schedules_campaigns_campaign_id

        Get a dialer campaign schedule.
        """
        pass

    def test_get_schedules_sequences(self):
        """
        Test case for get_schedules_sequences

        Query for a list of dialer sequence schedules.
        """
        pass

    def test_get_schedules_sequences_sequence_id(self):
        """
        Test case for get_schedules_sequences_sequence_id

        Get a dialer sequence schedule.
        """
        pass

    def test_get_sequences(self):
        """
        Test case for get_sequences

        Query a list of dialer campaign sequences.
        """
        pass

    def test_get_sequences_sequence_id(self):
        """
        Test case for get_sequences_sequence_id

        Get a dialer campaign sequence.
        """
        pass

    def test_get_wrapupcodemappings(self):
        """
        Test case for get_wrapupcodemappings

        Get the Dialer wrap up code mapping.
        """
        pass

    def test_post_audits(self):
        """
        Test case for post_audits

        Retrieves audits for dialer.
        """
        pass

    def test_post_callabletimesets(self):
        """
        Test case for post_callabletimesets

        Create callable time set
        """
        pass

    def test_post_callanalysisresponsesets(self):
        """
        Test case for post_callanalysisresponsesets

        Create a dialer call analysis response set.
        """
        pass

    def test_post_campaigns(self):
        """
        Test case for post_campaigns

        Create a campaign.
        """
        pass

    def test_post_campaigns_campaign_id_callback_schedule(self):
        """
        Test case for post_campaigns_campaign_id_callback_schedule

        Schedule a Callback for a Dialer Campaign
        """
        pass

    def test_post_campaigns_progress(self):
        """
        Test case for post_campaigns_progress

        Get progress for a list of campaigns
        """
        pass

    def test_post_contactlists(self):
        """
        Test case for post_contactlists

        Create a contact List.
        """
        pass

    def test_post_contactlists_contactlist_id_contacts(self):
        """
        Test case for post_contactlists_contactlist_id_contacts

        Add contacts to a contact list.
        """
        pass

    def test_post_contactlists_contactlist_id_export(self):
        """
        Test case for post_contactlists_contactlist_id_export

        Initiate the export of a contact list.
        """
        pass

    def test_post_conversations_conversation_id_dnc(self):
        """
        Test case for post_conversations_conversation_id_dnc

        Add phone numbers to a Dialer DNC list.
        """
        pass

    def test_post_dnclists(self):
        """
        Test case for post_dnclists

        Create dialer DNC list
        """
        pass

    def test_post_dnclists_dnclist_id_export(self):
        """
        Test case for post_dnclists_dnclist_id_export

        Initiate the export of a dnc list.
        """
        pass

    def test_post_dnclists_dnclist_id_phonenumbers(self):
        """
        Test case for post_dnclists_dnclist_id_phonenumbers

        Add phone numbers to a Dialer DNC list.
        """
        pass

    def test_post_rulesets(self):
        """
        Test case for post_rulesets

        Create a Dialer Call Analysis Response Set.
        """
        pass

    def test_post_sequences(self):
        """
        Test case for post_sequences

        Create a new campaign sequence.
        """
        pass

    def test_put_callabletimesets_callabletimeset_id(self):
        """
        Test case for put_callabletimesets_callabletimeset_id

        Update callable time set
        """
        pass

    def test_put_callanalysisresponsesets_callanalysisset_id(self):
        """
        Test case for put_callanalysisresponsesets_callanalysisset_id

        Update a dialer call analysis response set.
        """
        pass

    def test_put_campaigns_campaign_id(self):
        """
        Test case for put_campaigns_campaign_id

        Update a campaign.
        """
        pass

    def test_put_campaigns_campaign_id_agents_user_id(self):
        """
        Test case for put_campaigns_campaign_id_agents_user_id

        Send notification that an agent's state changed 
        """
        pass

    def test_put_contactlists_contactlist_id(self):
        """
        Test case for put_contactlists_contactlist_id

        Update a contact list.
        """
        pass

    def test_put_contactlists_contactlist_id_contacts_contact_id(self):
        """
        Test case for put_contactlists_contactlist_id_contacts_contact_id

        Update a contact.
        """
        pass

    def test_put_dnclists_dnclist_id(self):
        """
        Test case for put_dnclists_dnclist_id

        Update dialer DNC list
        """
        pass

    def test_put_rulesets_ruleset_id(self):
        """
        Test case for put_rulesets_ruleset_id

        Update a RuleSet.
        """
        pass

    def test_put_schedules_campaigns_campaign_id(self):
        """
        Test case for put_schedules_campaigns_campaign_id

        Update a new campaign schedule.
        """
        pass

    def test_put_schedules_sequences_sequence_id(self):
        """
        Test case for put_schedules_sequences_sequence_id

        Update a new sequence schedule.
        """
        pass

    def test_put_sequences_sequence_id(self):
        """
        Test case for put_sequences_sequence_id

        Update a new campaign sequence.
        """
        pass

    def test_put_wrapupcodemappings(self):
        """
        Test case for put_wrapupcodemappings

        Update the Dialer wrap up code mapping.
        """
        pass


if __name__ == '__main__':
    unittest.main()