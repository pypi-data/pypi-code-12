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
from swagger_client.apis.content_management_api import ContentManagementApi


class TestContentManagementApi(unittest.TestCase):
    """ ContentManagementApi unit test stubs """

    def setUp(self):
        self.api = swagger_client.apis.content_management_api.ContentManagementApi()

    def tearDown(self):
        pass

    def test_delete_documents_document_id(self):
        """
        Test case for delete_documents_document_id

        Delete a document.
        """
        pass

    def test_delete_shares_share_id(self):
        """
        Test case for delete_shares_share_id

        Deletes an existing share.
        """
        pass

    def test_delete_status_status_id(self):
        """
        Test case for delete_status_status_id

        Cancel the command for this status
        """
        pass

    def test_delete_workspaces_workspace_id(self):
        """
        Test case for delete_workspaces_workspace_id

        Delete a workspace
        """
        pass

    def test_delete_workspaces_workspace_id_members_member_id(self):
        """
        Test case for delete_workspaces_workspace_id_members_member_id

        Delete a member from a workspace
        """
        pass

    def test_delete_workspaces_workspace_id_tagvalues_tag_id(self):
        """
        Test case for delete_workspaces_workspace_id_tagvalues_tag_id

        Delete workspace tag
        """
        pass

    def test_get_documents(self):
        """
        Test case for get_documents

        Get a list of documents.
        """
        pass

    def test_get_documents_document_id(self):
        """
        Test case for get_documents_document_id

        Get a document.
        """
        pass

    def test_get_documents_document_id_audits(self):
        """
        Test case for get_documents_document_id_audits

        Get a list of audits for a document.
        """
        pass

    def test_get_documents_document_id_content(self):
        """
        Test case for get_documents_document_id_content

        Download a document.
        """
        pass

    def test_get_query(self):
        """
        Test case for get_query

        Query content
        """
        pass

    def test_get_securityprofiles(self):
        """
        Test case for get_securityprofiles

        Get a List of Security Profiles
        """
        pass

    def test_get_securityprofiles_securityprofile_id(self):
        """
        Test case for get_securityprofiles_securityprofile_id

        Get a Security Profile
        """
        pass

    def test_get_shared_shared_id(self):
        """
        Test case for get_shared_shared_id

        Get shared documents. Securely download a shared document.
        """
        pass

    def test_get_shares(self):
        """
        Test case for get_shares

        Gets a list of shares.  You must specify at least one filter (e.g. entityId).
        """
        pass

    def test_get_shares_share_id(self):
        """
        Test case for get_shares_share_id

        Retrieve details about an existing share.
        """
        pass

    def test_get_status(self):
        """
        Test case for get_status

        Get a list of statuses for pending operations
        """
        pass

    def test_get_status_status_id(self):
        """
        Test case for get_status_status_id

        Get a status.
        """
        pass

    def test_get_usage(self):
        """
        Test case for get_usage

        Get usage details.
        """
        pass

    def test_get_workspaces(self):
        """
        Test case for get_workspaces

        Get a list of workspaces.
        """
        pass

    def test_get_workspaces_workspace_id(self):
        """
        Test case for get_workspaces_workspace_id

        Get a workspace.
        """
        pass

    def test_get_workspaces_workspace_id_members(self):
        """
        Test case for get_workspaces_workspace_id_members

        Get a list workspace members
        """
        pass

    def test_get_workspaces_workspace_id_members_member_id(self):
        """
        Test case for get_workspaces_workspace_id_members_member_id

        Get a workspace member
        """
        pass

    def test_get_workspaces_workspace_id_tagvalues(self):
        """
        Test case for get_workspaces_workspace_id_tagvalues

        Get a list of workspace tags
        """
        pass

    def test_get_workspaces_workspace_id_tagvalues_tag_id(self):
        """
        Test case for get_workspaces_workspace_id_tagvalues_tag_id

        Get a workspace tag
        """
        pass

    def test_post_auditquery(self):
        """
        Test case for post_auditquery

        Query audits
        """
        pass

    def test_post_documents(self):
        """
        Test case for post_documents

        Add a document.
        """
        pass

    def test_post_documents_document_id(self):
        """
        Test case for post_documents_document_id

        Update a document.
        """
        pass

    def test_post_documents_document_id_content(self):
        """
        Test case for post_documents_document_id_content

        Replace the contents of a document.
        """
        pass

    def test_post_query(self):
        """
        Test case for post_query

        Query content
        """
        pass

    def test_post_shares(self):
        """
        Test case for post_shares

        Creates a new share or updates an existing share if the entity has already been shared
        """
        pass

    def test_post_workspaces(self):
        """
        Test case for post_workspaces

        Create a group workspace
        """
        pass

    def test_post_workspaces_workspace_id_tagvalues(self):
        """
        Test case for post_workspaces_workspace_id_tagvalues

        Create a workspace tag
        """
        pass

    def test_post_workspaces_workspace_id_tagvalues_query(self):
        """
        Test case for post_workspaces_workspace_id_tagvalues_query

        Perform a prefix query on tags in the workspace
        """
        pass

    def test_put_workspaces_workspace_id(self):
        """
        Test case for put_workspaces_workspace_id

        Update a workspace
        """
        pass

    def test_put_workspaces_workspace_id_members_member_id(self):
        """
        Test case for put_workspaces_workspace_id_members_member_id

        Add a member to a workspace
        """
        pass

    def test_put_workspaces_workspace_id_tagvalues_tag_id(self):
        """
        Test case for put_workspaces_workspace_id_tagvalues_tag_id

        Update a workspace tag. Will update all documents with the new tag value.
        """
        pass


if __name__ == '__main__':
    unittest.main()