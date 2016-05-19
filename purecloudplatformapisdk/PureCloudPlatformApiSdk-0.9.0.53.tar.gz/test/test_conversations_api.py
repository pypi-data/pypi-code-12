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
from swagger_client.apis.conversations_api import ConversationsApi


class TestConversationsApi(unittest.TestCase):
    """ ConversationsApi unit test stubs """

    def setUp(self):
        self.api = swagger_client.apis.conversations_api.ConversationsApi()

    def tearDown(self):
        pass

    def test_delete_calls_call_id_participants_participant_id_consult(self):
        """
        Test case for delete_calls_call_id_participants_participant_id_consult

        Cancel the transfer
        """
        pass

    def test_delete_emails_email_id_messages_draft_attachments_attachment_id(self):
        """
        Test case for delete_emails_email_id_messages_draft_attachments_attachment_id

        Delete attachment from draft
        """
        pass

    def test_get_callbacks(self):
        """
        Test case for get_callbacks

        Get callback conversations
        """
        pass

    def test_get_callbacks_callback_id(self):
        """
        Test case for get_callbacks_callback_id

        Get callback conversation
        """
        pass

    def test_get_callbacks_callback_id_participants_participant_id_wrapup(self):
        """
        Test case for get_callbacks_callback_id_participants_participant_id_wrapup

        Get the wrap-up for this conversation participant. 
        """
        pass

    def test_get_callbacks_callback_id_participants_participant_id_wrapupcodes(self):
        """
        Test case for get_callbacks_callback_id_participants_participant_id_wrapupcodes

        Get list of wrapup codes for this conversation participant
        """
        pass

    def test_get_calls(self):
        """
        Test case for get_calls

        Get recent conversations
        """
        pass

    def test_get_calls_call_id(self):
        """
        Test case for get_calls_call_id

        Get call conversation
        """
        pass

    def test_get_calls_call_id_participants_participant_id_wrapup(self):
        """
        Test case for get_calls_call_id_participants_participant_id_wrapup

        Get the wrap-up for this conversation participant. 
        """
        pass

    def test_get_calls_call_id_participants_participant_id_wrapupcodes(self):
        """
        Test case for get_calls_call_id_participants_participant_id_wrapupcodes

        Get list of wrapup codes for this conversation participant
        """
        pass

    def test_get_calls_history(self):
        """
        Test case for get_calls_history

        Get call history
        """
        pass

    def test_get_calls_maximumconferenceparties(self):
        """
        Test case for get_calls_maximumconferenceparties

        Get the maximum number of participants that this user can have on a conference
        """
        pass

    def test_get_chats(self):
        """
        Test case for get_chats

        Get recent chat conversations
        """
        pass

    def test_get_chats_chat_id(self):
        """
        Test case for get_chats_chat_id

        Get chat conversation
        """
        pass

    def test_get_chats_chat_id_participants_participant_id_wrapup(self):
        """
        Test case for get_chats_chat_id_participants_participant_id_wrapup

        Get the wrap-up for this conversation participant. 
        """
        pass

    def test_get_chats_chat_id_participants_participant_id_wrapupcodes(self):
        """
        Test case for get_chats_chat_id_participants_participant_id_wrapupcodes

        Get list of wrapup codes for this conversation participant
        """
        pass

    def test_get_conversation_id(self):
        """
        Test case for get_conversation_id

        Get conversation
        """
        pass

    def test_get_conversation_id_participants_participant_id_wrapup(self):
        """
        Test case for get_conversation_id_participants_participant_id_wrapup

        Get the wrap-up for this conversation participant. 
        """
        pass

    def test_get_conversation_id_participants_participant_id_wrapupcodes(self):
        """
        Test case for get_conversation_id_participants_participant_id_wrapupcodes

        Get list of wrapup codes for this conversation participant
        """
        pass

    def test_get_conversations(self):
        """
        Test case for get_conversations

        Get conversations
        """
        pass

    def test_get_conversations_conversation_id_details(self):
        """
        Test case for get_conversations_conversation_id_details

        Get a conversation by id
        """
        pass

    def test_get_emails(self):
        """
        Test case for get_emails

        Get recent email conversations
        """
        pass

    def test_get_emails_email_id(self):
        """
        Test case for get_emails_email_id

        Get email conversation
        """
        pass

    def test_get_emails_email_id_messages(self):
        """
        Test case for get_emails_email_id_messages

        Get conversation messages
        """
        pass

    def test_get_emails_email_id_messages_draft(self):
        """
        Test case for get_emails_email_id_messages_draft

        Get conversation draft reply
        """
        pass

    def test_get_emails_email_id_messages_message_id(self):
        """
        Test case for get_emails_email_id_messages_message_id

        Get conversation message
        """
        pass

    def test_get_emails_email_id_participants_participant_id_wrapup(self):
        """
        Test case for get_emails_email_id_participants_participant_id_wrapup

        Get the wrap-up for this conversation participant. 
        """
        pass

    def test_get_emails_email_id_participants_participant_id_wrapupcodes(self):
        """
        Test case for get_emails_email_id_participants_participant_id_wrapupcodes

        Get list of wrapup codes for this conversation participant
        """
        pass

    def test_patch_callbacks_callback_id_participants_participant_id(self):
        """
        Test case for patch_callbacks_callback_id_participants_participant_id

        Update conversation participant
        """
        pass

    def test_patch_callbacks_callback_id_participants_participant_id_attributes(self):
        """
        Test case for patch_callbacks_callback_id_participants_participant_id_attributes

        Update the attributes on a conversation participant.
        """
        pass

    def test_patch_calls_call_id(self):
        """
        Test case for patch_calls_call_id

        Update conversation
        """
        pass

    def test_patch_calls_call_id_participants_participant_id(self):
        """
        Test case for patch_calls_call_id_participants_participant_id

        Update conversation participant
        """
        pass

    def test_patch_calls_call_id_participants_participant_id_attributes(self):
        """
        Test case for patch_calls_call_id_participants_participant_id_attributes

        Update the attributes on a conversation participant.
        """
        pass

    def test_patch_calls_call_id_participants_participant_id_consult(self):
        """
        Test case for patch_calls_call_id_participants_participant_id_consult

        Change who can speak
        """
        pass

    def test_patch_chats_chat_id_participants_participant_id(self):
        """
        Test case for patch_chats_chat_id_participants_participant_id

        Update conversation participant
        """
        pass

    def test_patch_chats_chat_id_participants_participant_id_attributes(self):
        """
        Test case for patch_chats_chat_id_participants_participant_id_attributes

        Update the attributes on a conversation participant.
        """
        pass

    def test_patch_conversation_id_participants_participant_id(self):
        """
        Test case for patch_conversation_id_participants_participant_id

        Update a participant.
        """
        pass

    def test_patch_conversation_id_participants_participant_id_attributes(self):
        """
        Test case for patch_conversation_id_participants_participant_id_attributes

        Update the attributes on a conversation participant.
        """
        pass

    def test_patch_emails_email_id_participants_participant_id(self):
        """
        Test case for patch_emails_email_id_participants_participant_id

        Update conversation participant
        """
        pass

    def test_patch_emails_email_id_participants_participant_id_attributes(self):
        """
        Test case for patch_emails_email_id_participants_participant_id_attributes

        Update the attributes on a conversation participant.
        """
        pass

    def test_post_callbacks_callback_id_participants_participant_id_replace(self):
        """
        Test case for post_callbacks_callback_id_participants_participant_id_replace

        Replace this participant with the specified user and/or address
        """
        pass

    def test_post_calls(self):
        """
        Test case for post_calls

        Create a call conversation
        """
        pass

    def test_post_calls_call_id(self):
        """
        Test case for post_calls_call_id

        Add a new call to a conversation
        """
        pass

    def test_post_calls_call_id_participants(self):
        """
        Test case for post_calls_call_id_participants

        Add participants to a conversation
        """
        pass

    def test_post_calls_call_id_participants_participant_id_consult(self):
        """
        Test case for post_calls_call_id_participants_participant_id_consult

        Initiate and update consult transfer
        """
        pass

    def test_post_calls_call_id_participants_participant_id_monitor(self):
        """
        Test case for post_calls_call_id_participants_participant_id_monitor

        Listen in on the conversation from the point of view of a given participant.
        """
        pass

    def test_post_calls_call_id_participants_participant_id_replace(self):
        """
        Test case for post_calls_call_id_participants_participant_id_replace

        Replace this participant with the specified user and/or address
        """
        pass

    def test_post_chats_chat_id_participants_participant_id_replace(self):
        """
        Test case for post_chats_chat_id_participants_participant_id_replace

        Replace this participant with the specified user and/or address
        """
        pass

    def test_post_conversation_id_participants_participant_id_callbacks(self):
        """
        Test case for post_conversation_id_participants_participant_id_callbacks

        Create a new callback for the specified participant on the conversation.
        """
        pass

    def test_post_conversation_id_participants_participant_id_replace(self):
        """
        Test case for post_conversation_id_participants_participant_id_replace

        Replace this participant with the specified user and/or address
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

    def test_post_emails_email_id_messages(self):
        """
        Test case for post_emails_email_id_messages

        Send an email reply
        """
        pass

    def test_post_emails_email_id_participants_participant_id_replace(self):
        """
        Test case for post_emails_email_id_participants_participant_id_replace

        Replace this participant with the specified user and/or address
        """
        pass

    def test_post_faxes(self):
        """
        Test case for post_faxes

        Create Fax Conversation
        """
        pass

    def test_put_emails_email_id_messages_draft(self):
        """
        Test case for put_emails_email_id_messages_draft

        Update conversation draft reply
        """
        pass


if __name__ == '__main__':
    unittest.main()