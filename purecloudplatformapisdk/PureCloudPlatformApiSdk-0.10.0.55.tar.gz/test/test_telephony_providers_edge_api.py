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
from swagger_client.apis.telephony_providers_edge_api import TelephonyProvidersEdgeApi


class TestTelephonyProvidersEdgeApi(unittest.TestCase):
    """ TelephonyProvidersEdgeApi unit test stubs """

    def setUp(self):
        self.api = swagger_client.apis.telephony_providers_edge_api.TelephonyProvidersEdgeApi()

    def tearDown(self):
        pass

    def test_delete_providers_edges_certificateauthorities_certificate_id(self):
        """
        Test case for delete_providers_edges_certificateauthorities_certificate_id

        Delete a certificate authority.
        """
        pass

    def test_delete_providers_edges_didpools_didpool_id(self):
        """
        Test case for delete_providers_edges_didpools_didpool_id

        Delete a DID Pool by ID.
        """
        pass

    def test_delete_providers_edges_edge_id(self):
        """
        Test case for delete_providers_edges_edge_id

        Delete a edge.
        """
        pass

    def test_delete_providers_edges_edge_id_logicalinterfaces_interface_id(self):
        """
        Test case for delete_providers_edges_edge_id_logicalinterfaces_interface_id

        Delete an edge logical interface
        """
        pass

    def test_delete_providers_edges_edge_id_softwareupdate(self):
        """
        Test case for delete_providers_edges_edge_id_softwareupdate

        Cancels any in-progress update for this edge.
        """
        pass

    def test_delete_providers_edges_edgegroups_edgegroup_id(self):
        """
        Test case for delete_providers_edges_edgegroups_edgegroup_id

        Delete an edge group.
        """
        pass

    def test_delete_providers_edges_endpoints_endpoint_id(self):
        """
        Test case for delete_providers_edges_endpoints_endpoint_id

        Delete endpoint
        """
        pass

    def test_delete_providers_edges_extensionpools_extensionpool_id(self):
        """
        Test case for delete_providers_edges_extensionpools_extensionpool_id

        Delete an extension pool by ID
        """
        pass

    def test_delete_providers_edges_outboundroutes_outboundroute_id(self):
        """
        Test case for delete_providers_edges_outboundroutes_outboundroute_id

        Delete Outbound Route
        """
        pass

    def test_delete_providers_edges_phonebasesettings_phonebase_id(self):
        """
        Test case for delete_providers_edges_phonebasesettings_phonebase_id

        Delete a Phone Base Settings by ID
        """
        pass

    def test_delete_providers_edges_phones_phone_id(self):
        """
        Test case for delete_providers_edges_phones_phone_id

        Delete a Phone by ID
        """
        pass

    def test_delete_providers_edges_sites_site_id(self):
        """
        Test case for delete_providers_edges_sites_site_id

        Delete an ednpoint
        """
        pass

    def test_delete_providers_edges_trunkbasesettings_trunkbasesettings_id(self):
        """
        Test case for delete_providers_edges_trunkbasesettings_trunkbasesettings_id

        Delete a Trunk Base Settings object by ID
        """
        pass

    def test_get_providers_edges(self):
        """
        Test case for get_providers_edges

        Get the list of edges.
        """
        pass

    def test_get_providers_edges_availablelanguages(self):
        """
        Test case for get_providers_edges_availablelanguages

        Get the list of available languages.
        """
        pass

    def test_get_providers_edges_certificateauthorities(self):
        """
        Test case for get_providers_edges_certificateauthorities

        Get the list of certificate authorities.
        """
        pass

    def test_get_providers_edges_certificateauthorities_certificate_id(self):
        """
        Test case for get_providers_edges_certificateauthorities_certificate_id

        Get a certificate authority.
        """
        pass

    def test_get_providers_edges_didpools(self):
        """
        Test case for get_providers_edges_didpools

        Get a listing of DID Pools
        """
        pass

    def test_get_providers_edges_didpools_didpool_id(self):
        """
        Test case for get_providers_edges_didpools_didpool_id

        Get a DID Pool by ID.
        """
        pass

    def test_get_providers_edges_dids(self):
        """
        Test case for get_providers_edges_dids

        Get a listing of DIDs
        """
        pass

    def test_get_providers_edges_dids_did_id(self):
        """
        Test case for get_providers_edges_dids_did_id

        Get a DID by ID.
        """
        pass

    def test_get_providers_edges_edge_id(self):
        """
        Test case for get_providers_edges_edge_id

        Get edge.
        """
        pass

    def test_get_providers_edges_edge_id_lines(self):
        """
        Test case for get_providers_edges_edge_id_lines

        Get the list of lines.
        """
        pass

    def test_get_providers_edges_edge_id_lines_line_id(self):
        """
        Test case for get_providers_edges_edge_id_lines_line_id

        Get line
        """
        pass

    def test_get_providers_edges_edge_id_logicalinterfaces(self):
        """
        Test case for get_providers_edges_edge_id_logicalinterfaces

        Get edge logical interfaces.
        """
        pass

    def test_get_providers_edges_edge_id_logicalinterfaces_interface_id(self):
        """
        Test case for get_providers_edges_edge_id_logicalinterfaces_interface_id

        Get an edge logical interface
        """
        pass

    def test_get_providers_edges_edge_id_logs_jobs_job_id(self):
        """
        Test case for get_providers_edges_edge_id_logs_jobs_job_id

        Get an Edge logs job.
        """
        pass

    def test_get_providers_edges_edge_id_physicalinterfaces(self):
        """
        Test case for get_providers_edges_edge_id_physicalinterfaces

        Retrieve a list of all configured physical interfaces from a specific edge.
        """
        pass

    def test_get_providers_edges_edge_id_physicalinterfaces_interface_id(self):
        """
        Test case for get_providers_edges_edge_id_physicalinterfaces_interface_id

        Get edge physical interface.
        """
        pass

    def test_get_providers_edges_edge_id_softwareupdate(self):
        """
        Test case for get_providers_edges_edge_id_softwareupdate

        Gets software update status information about any edge.
        """
        pass

    def test_get_providers_edges_edge_id_softwareversions(self):
        """
        Test case for get_providers_edges_edge_id_softwareversions

        Gets all the available software versions for this edge.
        """
        pass

    def test_get_providers_edges_edgegroups(self):
        """
        Test case for get_providers_edges_edgegroups

        Get the list of edge groups.
        """
        pass

    def test_get_providers_edges_edgegroups_edgegroup_id(self):
        """
        Test case for get_providers_edges_edgegroups_edgegroup_id

        Get edge group.
        """
        pass

    def test_get_providers_edges_edgeversionreport(self):
        """
        Test case for get_providers_edges_edgeversionreport

        Get the edge version report.
        """
        pass

    def test_get_providers_edges_endpoints(self):
        """
        Test case for get_providers_edges_endpoints

        Get endpoints
        """
        pass

    def test_get_providers_edges_endpoints_endpoint_id(self):
        """
        Test case for get_providers_edges_endpoints_endpoint_id

        Get endpoint
        """
        pass

    def test_get_providers_edges_extensionpools(self):
        """
        Test case for get_providers_edges_extensionpools

        Get a listing of extension pools
        """
        pass

    def test_get_providers_edges_extensionpools_extensionpool_id(self):
        """
        Test case for get_providers_edges_extensionpools_extensionpool_id

        Get an extension pool by ID
        """
        pass

    def test_get_providers_edges_extensions(self):
        """
        Test case for get_providers_edges_extensions

        Get a listing of extensions
        """
        pass

    def test_get_providers_edges_extensions_extension_id(self):
        """
        Test case for get_providers_edges_extensions_extension_id

        Get an extension by ID.
        """
        pass

    def test_get_providers_edges_linebasesettings(self):
        """
        Test case for get_providers_edges_linebasesettings

        Get a listing of line base settings objects
        """
        pass

    def test_get_providers_edges_linebasesettings_linebase_id(self):
        """
        Test case for get_providers_edges_linebasesettings_linebase_id

        Get a line base settings object by ID
        """
        pass

    def test_get_providers_edges_lines(self):
        """
        Test case for get_providers_edges_lines

        Get a list of Lines
        """
        pass

    def test_get_providers_edges_lines_line_id(self):
        """
        Test case for get_providers_edges_lines_line_id

        Get a Line by ID
        """
        pass

    def test_get_providers_edges_lines_template(self):
        """
        Test case for get_providers_edges_lines_template

        Get a Line instance template based on a Line Base Settings object. This object can then be modified and saved as a new Line instance
        """
        pass

    def test_get_providers_edges_outboundroutes(self):
        """
        Test case for get_providers_edges_outboundroutes

        Get outbound routes
        """
        pass

    def test_get_providers_edges_outboundroutes_outboundroute_id(self):
        """
        Test case for get_providers_edges_outboundroutes_outboundroute_id

        Get outbound route
        """
        pass

    def test_get_providers_edges_phonebasesettings(self):
        """
        Test case for get_providers_edges_phonebasesettings

        Get a list of Phone Base Settings objects
        """
        pass

    def test_get_providers_edges_phonebasesettings_availablemetabases(self):
        """
        Test case for get_providers_edges_phonebasesettings_availablemetabases

        Get a list of available makes and models to create a new Phone Base Settings
        """
        pass

    def test_get_providers_edges_phonebasesettings_phonebase_id(self):
        """
        Test case for get_providers_edges_phonebasesettings_phonebase_id

        Get a Phone Base Settings object by ID
        """
        pass

    def test_get_providers_edges_phonebasesettings_template(self):
        """
        Test case for get_providers_edges_phonebasesettings_template

        Get a Phone Base Settings instance template from a given make and model. This object can then be modified and saved as a new Phone Base Settings instance
        """
        pass

    def test_get_providers_edges_phones(self):
        """
        Test case for get_providers_edges_phones

        Get a list of Phone Instances
        """
        pass

    def test_get_providers_edges_phones_phone_id(self):
        """
        Test case for get_providers_edges_phones_phone_id

        Get a Phone by ID
        """
        pass

    def test_get_providers_edges_phones_template(self):
        """
        Test case for get_providers_edges_phones_template

        Get a Phone instance template based on a Phone Base Settings object. This object can then be modified and saved as a new Phone instance
        """
        pass

    def test_get_providers_edges_sites(self):
        """
        Test case for get_providers_edges_sites

        Get the list of sites.
        """
        pass

    def test_get_providers_edges_sites_site_id(self):
        """
        Test case for get_providers_edges_sites_site_id

        Get endpoint.
        """
        pass

    def test_get_providers_edges_sites_site_id_numberplans(self):
        """
        Test case for get_providers_edges_sites_site_id_numberplans

        Get the list of Number Plans for this Site.
        """
        pass

    def test_get_providers_edges_sites_site_id_numberplans_classifications(self):
        """
        Test case for get_providers_edges_sites_site_id_numberplans_classifications

        Get a list of Classifications for this Site
        """
        pass

    def test_get_providers_edges_sites_site_id_numberplans_numberplan_id(self):
        """
        Test case for get_providers_edges_sites_site_id_numberplans_numberplan_id

        Get a Number Plan by ID.
        """
        pass

    def test_get_providers_edges_timezones(self):
        """
        Test case for get_providers_edges_timezones

        Get a list of Edge-compatible time zones
        """
        pass

    def test_get_providers_edges_trunkbasesettings(self):
        """
        Test case for get_providers_edges_trunkbasesettings

        Get Trunk Base Settings listing
        """
        pass

    def test_get_providers_edges_trunkbasesettings_availablemetabases(self):
        """
        Test case for get_providers_edges_trunkbasesettings_availablemetabases

        Get a list of available makes and models to create a new Trunk Base Settings
        """
        pass

    def test_get_providers_edges_trunkbasesettings_template(self):
        """
        Test case for get_providers_edges_trunkbasesettings_template

        Get a Trunk Base Settings instance template from a given make and model. This object can then be modified and saved as a new Trunk Base Settings instance
        """
        pass

    def test_get_providers_edges_trunkbasesettings_trunkbasesettings_id(self):
        """
        Test case for get_providers_edges_trunkbasesettings_trunkbasesettings_id

        Get a Trunk Base Settings object by ID
        """
        pass

    def test_get_providers_edges_trunks(self):
        """
        Test case for get_providers_edges_trunks

        Get the list of available trunks.
        """
        pass

    def test_get_providers_edges_trunks_trunk_id(self):
        """
        Test case for get_providers_edges_trunks_trunk_id

        Get a Trunk by ID
        """
        pass

    def test_get_providers_edges_trunkswithrecording(self):
        """
        Test case for get_providers_edges_trunkswithrecording

        Get Counts of trunks that have recording disabled or enabled
        """
        pass

    def test_get_schemas_edges_vnext(self):
        """
        Test case for get_schemas_edges_vnext

        Lists available schema categories
        """
        pass

    def test_get_schemas_edges_vnext_schemacategory(self):
        """
        Test case for get_schemas_edges_vnext_schemacategory

        List schemas of a specific category
        """
        pass

    def test_get_schemas_edges_vnext_schemacategory_schematype(self):
        """
        Test case for get_schemas_edges_vnext_schemacategory_schematype

        List schemas of a specific category
        """
        pass

    def test_get_schemas_edges_vnext_schemacategory_schematype_schema_id(self):
        """
        Test case for get_schemas_edges_vnext_schemacategory_schematype_schema_id

        Get a json schema
        """
        pass

    def test_get_schemas_edges_vnext_schemacategory_schematype_schema_id_extensiontype_metadata_id(self):
        """
        Test case for get_schemas_edges_vnext_schemacategory_schematype_schema_id_extensiontype_metadata_id

        Get metadata for a schema
        """
        pass

    def test_post_providers_edges(self):
        """
        Test case for post_providers_edges

        Create a edge.
        """
        pass

    def test_post_providers_edges_addressvalidation(self):
        """
        Test case for post_providers_edges_addressvalidation

        Validates a street address
        """
        pass

    def test_post_providers_edges_certificateauthorities(self):
        """
        Test case for post_providers_edges_certificateauthorities

        Create a certificate authority.
        """
        pass

    def test_post_providers_edges_didpools(self):
        """
        Test case for post_providers_edges_didpools

        Create a new DID pool
        """
        pass

    def test_post_providers_edges_edge_id_logicalinterfaces(self):
        """
        Test case for post_providers_edges_edge_id_logicalinterfaces

        Create an edge logical interface.
        """
        pass

    def test_post_providers_edges_edge_id_logs_jobs(self):
        """
        Test case for post_providers_edges_edge_id_logs_jobs

        Create a job to upload a list of Edge logs.
        """
        pass

    def test_post_providers_edges_edge_id_logs_jobs_job_id_upload(self):
        """
        Test case for post_providers_edges_edge_id_logs_jobs_job_id_upload

        Request that the specified fileIds be uploaded from the Edge.
        """
        pass

    def test_post_providers_edges_edge_id_reboot(self):
        """
        Test case for post_providers_edges_edge_id_reboot

        Reboot an Edge
        """
        pass

    def test_post_providers_edges_edge_id_softwareupdate(self):
        """
        Test case for post_providers_edges_edge_id_softwareupdate

        Starts a software update for this edge.
        """
        pass

    def test_post_providers_edges_edge_id_unpair(self):
        """
        Test case for post_providers_edges_edge_id_unpair

        Unpair an Edge
        """
        pass

    def test_post_providers_edges_edgegroups(self):
        """
        Test case for post_providers_edges_edgegroups

        Create an edge group.
        """
        pass

    def test_post_providers_edges_endpoints(self):
        """
        Test case for post_providers_edges_endpoints

        Create endpoint
        """
        pass

    def test_post_providers_edges_extensionpools(self):
        """
        Test case for post_providers_edges_extensionpools

        Create a new extension pool
        """
        pass

    def test_post_providers_edges_outboundroutes(self):
        """
        Test case for post_providers_edges_outboundroutes

        Create outbound rule
        """
        pass

    def test_post_providers_edges_phonebasesettings(self):
        """
        Test case for post_providers_edges_phonebasesettings

        Create a new Phone Base Settings object
        """
        pass

    def test_post_providers_edges_phones(self):
        """
        Test case for post_providers_edges_phones

        Create a new Phone
        """
        pass

    def test_post_providers_edges_phones_phone_id_reboot(self):
        """
        Test case for post_providers_edges_phones_phone_id_reboot

        Reboot a Phone
        """
        pass

    def test_post_providers_edges_phones_reboot(self):
        """
        Test case for post_providers_edges_phones_reboot

        Reboot Multiple Phones
        """
        pass

    def test_post_providers_edges_sites(self):
        """
        Test case for post_providers_edges_sites

        Create a endpoint.
        """
        pass

    def test_post_providers_edges_sites_site_id_rebalance(self):
        """
        Test case for post_providers_edges_sites_site_id_rebalance

        Triggers the rebalance operation.
        """
        pass

    def test_post_providers_edges_trunkbasesettings(self):
        """
        Test case for post_providers_edges_trunkbasesettings

        Create a Trunk Base Settings object
        """
        pass

    def test_put_providers_edges_certificateauthorities_certificate_id(self):
        """
        Test case for put_providers_edges_certificateauthorities_certificate_id

        Update a certificate authority.
        """
        pass

    def test_put_providers_edges_didpools_didpool_id(self):
        """
        Test case for put_providers_edges_didpools_didpool_id

        Update a DID Pool by ID.
        """
        pass

    def test_put_providers_edges_dids_did_id(self):
        """
        Test case for put_providers_edges_dids_did_id

        Update a DID by ID.
        """
        pass

    def test_put_providers_edges_edge_id(self):
        """
        Test case for put_providers_edges_edge_id

        Update a edge.
        """
        pass

    def test_put_providers_edges_edge_id_lines_line_id(self):
        """
        Test case for put_providers_edges_edge_id_lines_line_id

        Update a line.
        """
        pass

    def test_put_providers_edges_edge_id_logicalinterfaces_interface_id(self):
        """
        Test case for put_providers_edges_edge_id_logicalinterfaces_interface_id

        Update an edge logical interface.
        """
        pass

    def test_put_providers_edges_edgegroups_edgegroup_id(self):
        """
        Test case for put_providers_edges_edgegroups_edgegroup_id

        Update an edge group.
        """
        pass

    def test_put_providers_edges_endpoints_endpoint_id(self):
        """
        Test case for put_providers_edges_endpoints_endpoint_id

        Update endpoint
        """
        pass

    def test_put_providers_edges_extensionpools_extensionpool_id(self):
        """
        Test case for put_providers_edges_extensionpools_extensionpool_id

        Update an extension pool by ID
        """
        pass

    def test_put_providers_edges_extensions_extension_id(self):
        """
        Test case for put_providers_edges_extensions_extension_id

        Update an extension by ID.
        """
        pass

    def test_put_providers_edges_outboundroutes_outboundroute_id(self):
        """
        Test case for put_providers_edges_outboundroutes_outboundroute_id

        Update outbound route
        """
        pass

    def test_put_providers_edges_phonebasesettings_phonebase_id(self):
        """
        Test case for put_providers_edges_phonebasesettings_phonebase_id

        Update a Phone Base Settings by ID
        """
        pass

    def test_put_providers_edges_phones_phone_id(self):
        """
        Test case for put_providers_edges_phones_phone_id

        Update a Phone by ID
        """
        pass

    def test_put_providers_edges_sites_site_id(self):
        """
        Test case for put_providers_edges_sites_site_id

        Update a endpoint.
        """
        pass

    def test_put_providers_edges_sites_site_id_numberplans(self):
        """
        Test case for put_providers_edges_sites_site_id_numberplans

        Update the list of Number Plans.
        """
        pass

    def test_put_providers_edges_trunkbasesettings_trunkbasesettings_id(self):
        """
        Test case for put_providers_edges_trunkbasesettings_trunkbasesettings_id

        Update a Trunk Base Settings object by ID
        """
        pass


if __name__ == '__main__':
    unittest.main()