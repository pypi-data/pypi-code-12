import unittest

import psychic_disco.api_gateway_config as agc
from .fake_gateway import FakeApiGatewayConsole


class TestApiGatewayConfig(unittest.TestCase):
    def setUp(self):
        agc.console = FakeApiGatewayConsole()

    def test_fetch_api_by_name(self):
        # agc.console.apis["good_api"] = RestApi.find("good_api")
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


if __name__ == "__main__":
    unittest.main()
