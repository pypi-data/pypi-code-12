""" Tests for seed_services_cli.stage_based_messaging """

from unittest import TestCase
from click.testing import CliRunner
from seed_services_cli.main import cli


class TestStageBasedMessagingCommands(TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def tearDown(self):
        pass

    def test_schedule_list_help(self):
        result = self.runner.invoke(cli, ['sbm-schedules', '--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(
            "List all schedules"
            in result.output)

    def test_messageset_list_help(self):
        result = self.runner.invoke(cli, ['sbm-messagesets', '--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(
            "List all messagesets"
            in result.output)

    def test_message_list_help(self):
        result = self.runner.invoke(cli, ['sbm-messages', '--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(
            "List all messages"
            in result.output)

    def test_message_delete_help(self):
        result = self.runner.invoke(cli, ['sbm-messages-delete', '--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(
            "Delete all messages matching filter"
            in result.output)

    def test_messages_import_help(self):
        result = self.runner.invoke(cli, ['sbm-messages-import', '--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(
            "Import to the Stage Based Messaging service."
            in result.output)
