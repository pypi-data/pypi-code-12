import unittest
import unittest.mock as mock
from preggy import expect

from tsuru_router_tailer.sender import Sender


class TestSender(unittest.TestCase):

    def setUp(self):
        self.sender = Sender()

    def test_should_have_a_default_host_and_port(self):
        expect(self.sender.host).to_equal('localhost')
        expect(self.sender.port).to_equal(420)

    def test_should_send_message(self):
        self.sender.sock = mock.Mock()
        self.sender.send({'a': 1})
        self.sender.sock.sendto.assert_called_once_with(
            b'{"a":1}',
            ('localhost', 420)
        )
