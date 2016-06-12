import unittest

from psychic_disco.rest_resource import RestResource
from psychic_disco.rest_api import RestApi


class TestRestResource(unittest.TestCase):
    def test_rest_resource_not_exists(self):
        resource = RestResource('/dummies')
        self.assertFalse(resource.exists_in_aws)

    def test_rest_resource_exists(self):
        api = RestApi.find("dummy-manager")
        resource = RestResource('/dummies')
        resource.aws_id = "123resourceid"
        resource.api = api
        self.assertTrue(resource.exists_in_aws)

    def test_rest_resource_fetch_from_aws(self):
        api = RestApi.find("dummy-manager")
        resource = RestResource('/dummies')
        resource.aws_id = "123resourceid"
        resource.api = api

        self.assertEqual(0, len(resource.methods))
        resource.fetch_from_aws()
        self.assertEqual(1, len(resource.methods))

    def test_rest_resource_path_part(self):
        api = RestApi.find("dummy-manager")
        resource = RestResource('/dummies/by_name')
        resource.api = api
        self.assertEqual(resource.path_part, "by_name")
