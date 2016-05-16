import unittest
import psychic_disco.api_gateway_config as agc
import json
import os


class FakeApiGatewayConsole(object):
    def __init__(self):
        self.apis = dict()
        self.basepath = os.path.dirname(os.path.abspath(__file__))

    def _open_json(self, filename):
        path = os.path.join(self.basepath, filename)
        with open(path) as f:
            return json.loads(f.read())

    def get_rest_apis(self):
        return self._open_json("get_rest_apis.json")

    def get_resources(self, **kwargs):
        return self._open_json("get-resources.json")

    def get_resource(self, **kwargs):
        return self._open_json("get-resource.json")

    def get_method(self, **kwargs):
        return self._open_json("get-method.json")


class TestApiGatewayConfig(unittest.TestCase):
    def setUp(self):
        agc.console = FakeApiGatewayConsole()

    def test_fetch_api_by_name(self):
        agc.console.apis["good_api"] = agc.RestApi.find("good_api")
        actual = agc.fetch_api_by_name("dummy-manager")
        self.assertEqual("123apiid", actual['id'])

    def test_fetch_wrong_api_name(self):
        actual = agc.fetch_api_by_name("an api has no name")
        self.assertIsNone(actual)

    def test_fetch_resources_by_api(self):
        actual = agc.fetch_resources_by_api("123apiid")
        self.assertEqual(2, len(actual))
        self.assertEqual("/", actual[0]['path'])
        self.assertEqual("/dummies", actual[1]['path'])

    def test_fetch_resource(self):
        actual = agc.fetch_resource("123apiid", "123resourceid")
        self.assertEqual({}, actual['resourceMethods']['post'])

    def test_fetch_method(self):
        actual = agc.fetch_method("123apiid", "123resourceid", "post")
        uri = actual['methodIntegration']['uri']
        expected_ending = "psychic_disco-dummy_lambda_function/invocations"
        self.assertTrue(uri.endswith(expected_ending))

    def test_lambda_arn_from_method_integration_arn(self):
        method = agc.console._open_json("get-method.json")
        uri = method['methodIntegration']['uri']
        expected_arn = "arn:aws:lambda:us-east-1:123456789012:function:psychic_disco-dummy_lambda_function"  # noqa
        actual_arn = agc.lambda_arn_from_method_integration_arn(uri)
        self.assertEqual(expected_arn, actual_arn)

    def test_lambda_name_from_lambda_arn(self):
        arn = "arn:aws:lambda:us-east-1:123456789012:function:psychic_disco-dummy_lambda_function"  # noqa
        expected_name = "psychic_disco-dummy_lambda_function"
        actual_name = agc.lambda_name_from_lambda_arn(arn)
        self.assertEqual(expected_name, actual_name)

    def test_rest_api_find(self):
        api = agc.RestApi.find("dummy-manager")
        self.assertEqual("123apiid", api.aws_id)
        self.assertTrue(api.exists_in_aws)
        self.assertEqual(2, len(api.resources))
        self.assertIn('/', api.resources)
        self.assertIn('/dummies', api.resources)

    def test_rest_resource_not_exists(self):
        resource = agc.RestResource('/dummies')
        self.assertFalse(resource.exists_in_aws)

    def test_rest_resource_exists(self):
        api = agc.RestApi.find("dummy-manager")
        resource = agc.RestResource('/dummies')
        resource.aws_id = "123resourceid"
        resource.api = api
        self.assertTrue(resource.exists_in_aws)

    def test_rest_resource_fetch_from_aws(self):
        api = agc.RestApi.find("dummy-manager")
        resource = agc.RestResource('/dummies')
        resource.aws_id = "123resourceid"
        resource.api = api

        self.assertEqual(0, len(resource.methods))
        resource.fetch_from_aws()
        self.assertEqual(1, len(resource.methods))

    def test_method_fetch_from_aws(self):
        method = agc.RestMethod('post')
        method.resource = agc.RestResource('/dummies')
        method.resource.aws_id = "123resourceid"
        method.resource.api = agc.RestApi.find("dummy-manager")
        method.api = method.resource.api

        self.assertIsNone(method.lambda_name)
        method.fetch_from_aws()
        self.assertEqual(
                "psychic_disco-dummy_lambda_function",
                method.lambda_name)


if __name__ == "__main__":
    unittest.main()
