import os
import sys
import mock
from ubackup.tests import TestCase
from ubackup.cli import main
from ubackup.cli.actions import dicover_commands
from ubackup.cli.utils import dropbox_token_flow


class CliTest(TestCase):

    @mock.patch('sys.exit')
    @mock.patch('ubackup.log.set_config')
    @mock.patch('ubackup.log.set_level')
    def test_cli(self, *args, **kwargs):
        with open(os.path.join(self.tmp_dir, 'foo'), 'w') as fp:
            fp.write('bar')

        sys.argv = [
            None,
            '--bucket=dropbox',
            'backup',
            'path',
            '--path=%s' % self.tmp_dir]
        main()

    def test_discover_commands(self):
        dicover_commands()

    @mock.patch('requests.post')
    @mock.patch('click.prompt')
    @mock.patch('click.pause')
    @mock.patch('click.launch')
    def test_dropbox_token_flow(self, mock_launch, mock_pause, mock_prompt, *args, **kwargs):
        dropbox_token_flow()
        self.assertTrue(mock_launch.called)
        self.assertTrue(mock_pause.called)
        self.assertTrue(mock_prompt.called)
