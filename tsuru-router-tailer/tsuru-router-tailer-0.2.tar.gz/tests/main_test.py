import sys
import unittest
import unittest.mock as mock

from tsuru_router_tailer.main import main


class TestMain(unittest.TestCase):

    @mock.patch('tsuru_router_tailer.runner.Runner')
    def test_call_runner(self, runner_mock):
        with mock.patch.object(sys, 'argv', [
                '',
                '--logstash', 'localhost:420',
                '/much/path',
        ]):
            main()
        runner_mock.assert_called_once_with(
            log_path='/much/path',
            logstash='localhost:420'
        )
