import unittest

from psychic_disco.rest_method import RestMethod
from psychic_disco.rest_resource import RestResource
from psychic_disco.rest_api import RestApi


class TestRestMethod(unittest.TestCase):
    def test_fetch_from_aws(self):
        method = RestMethod('post')
        method.resource = RestResource('/dummies')
        method.resource.aws_id = "123resourceid"
        method.resource.api = RestApi.find("dummy-manager")
        method.api = method.resource.api

        self.assertIsNone(method.lambda_name)
        method.fetch_from_aws()
        self.assertEqual(
                "psychic_disco-dummy_lambda_function",
                method.lambda_name)
