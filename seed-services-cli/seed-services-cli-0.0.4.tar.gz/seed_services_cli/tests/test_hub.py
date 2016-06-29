""" Tests for seed_services_cli.hub """

from unittest import TestCase
from click.testing import CliRunner
from seed_services_cli.main import cli


class TestSendCommand(TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def tearDown(self):
        pass

    def test_registration_import_get_help(self):
        result = self.runner.invoke(
            cli, ['hub-registrations-import', '--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(
            "Import registrations to the hub service."
            in result.output)
