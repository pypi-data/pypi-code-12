import unittest
import unittest.mock as mock

from tsuru_router_tailer.runner import Runner


class TestRunner(unittest.TestCase):

    def test_should_have_a_default_host_and_port(self):
        loop_mock = mock.Mock()
        with mock.patch('asyncio.get_event_loop', return_value=loop_mock):
            Runner('/dev/random', 'localhost:420', 'localhost:6379').run()
        assert loop_mock.run_until_complete.called
