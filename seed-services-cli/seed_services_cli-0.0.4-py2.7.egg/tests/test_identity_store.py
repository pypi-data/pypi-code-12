""" Tests for seed_services_cli.identity_store """

from unittest import TestCase
from click.testing import CliRunner
from seed_services_cli.main import cli
import responses


class TestSendCommand(TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def tearDown(self):
        pass

    def invoke_identity_search(self, args, address_type="msisdn",
                               address="+27001"):
        return self.runner.invoke(cli, [
            'identity-search',
            '--address_type', address_type,
            '--address', address,
        ] + args)

    def invoke_identity_get(self, args, identity="uuid"):
        return self.runner.invoke(cli, [
            'identity-get',
            '--identity', identity
        ] + args)

    def test_identity_search_help(self):
        result = self.runner.invoke(cli, ['identity-search', '--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(
            "Find an identity"
            in result.output)

    def test_identity_search_no_search_details(self):
        result = self.runner.invoke(cli, ['identity-search'])
        self.assertEqual(result.exit_code, 2)
        self.assertTrue(
            "Please specify address type and address. See --help."
            in result.output)

    # Can not get this to work
    @responses.activate
    def test_identity_search(self):
        # setup
        search_response = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": "0c03d360-1180-4fb4-9eed-ecd2cff8fa05",
                    "version": 1,
                    "details": {
                        "default_addr_type": "msisdn",
                        "addresses": {
                          "msisdn": {
                              "+27123": {}
                          }
                        }
                    }
                }
            ]
        }
        responses.add(responses.GET,
                      "http://id.example.org/api/v1/identities/search/?details__addresses__msisdn=%2B27001",  # noqa
                      json=search_response, status=200,
                      match_querystring=True)
        # Execute
        result = self.invoke_identity_search([])
        # Check
        self.assertEqual(result.exit_code, 0)
        self.assertTrue("Looking for msisdn of +27001." in result.output)
        self.assertTrue("Found 1 results:" in result.output)
        self.assertTrue("0c03d360-1180-4fb4-9eed-ecd2cff8fa05"
                        in result.output)
        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(responses.calls[0].request.url,
                        "http://id.example.org/api/v1/identities/search/?details__addresses__msisdn=%2B27001")  # noqa

    def test_identity_get_help(self):
        result = self.runner.invoke(cli, ['identity-get', '--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(
            "Find a specific identity"
            in result.output)

    def test_identity_get_no_identity_details(self):
        result = self.runner.invoke(cli, ['identity-get'])
        self.assertEqual(result.exit_code, 2)
        self.assertTrue(
            "Please specify identity UUID. See --help."
            in result.output)

    # Can not get this to work
    @responses.activate
    def test_identity_get(self):
        # setup
        get_response = {
            "id": "0c03d360-1180-4fb4-9eed-ecd2cff8fa05",
            "version": 1,
            "details": {
                "default_addr_type": "msisdn",
                "addresses": {
                  "msisdn": {
                      "+27123": {}
                  }
                }
            }
        }
        responses.add(responses.GET,
                      "http://id.example.org/api/v1/identities/0c03d360-1180-4fb4-9eed-ecd2cff8fa05/",  # noqa
                      json=get_response, status=200,
                      match_querystring=True)
        # Execute
        result = self.invoke_identity_get(
            [], identity="0c03d360-1180-4fb4-9eed-ecd2cff8fa05")
        # Check
        self.assertEqual(result.exit_code, 0)
        self.assertTrue('"id": "0c03d360-1180-4fb4-9eed-ecd2cff8fa05"'
                        in result.output)
        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(responses.calls[0].request.url,
                        "http://id.example.org/api/v1/identities/0c03d360-1180-4fb4-9eed-ecd2cff8fa05/")  # noqa

    def test_identity_import_get_help(self):
        result = self.runner.invoke(cli, ['identity-import', '--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(
            "Import to the Identity Store service."
            in result.output)
