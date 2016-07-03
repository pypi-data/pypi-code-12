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
from swagger_client.apis.fax_api import FaxApi


class TestFaxApi(unittest.TestCase):
    """ FaxApi unit test stubs """

    def setUp(self):
        self.api = swagger_client.apis.fax_api.FaxApi()

    def tearDown(self):
        pass

    def test_delete_documents_document_id(self):
        """
        Test case for delete_documents_document_id

        Delete a fax document.
        """
        pass

    def test_get_documents(self):
        """
        Test case for get_documents

        Get a list of fax documents.
        """
        pass

    def test_get_documents_document_id(self):
        """
        Test case for get_documents_document_id

        Get a document.
        """
        pass

    def test_get_documents_document_id_content(self):
        """
        Test case for get_documents_document_id_content

        Download a fax document.
        """
        pass

    def test_get_summary(self):
        """
        Test case for get_summary

        Get fax summary
        """
        pass

    def test_put_documents_document_id(self):
        """
        Test case for put_documents_document_id

        Update a fax document.
        """
        pass


if __name__ == '__main__':
    unittest.main()