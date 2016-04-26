from unittest import TestCase
from messaging_client.client_socket import ClientSocket
from messaging_client.messaging_client import MessagingClient


class DummySocket(ClientSocket):

    def __init__(self):
        super().__init__()
        self.sent_message = None
        self.receive_called = False
        self.connected = False

    def connect(self, host, port):
        self.connected = True

    def print_debug_message(self):
        pass

    def send(self, message):
        self.sent_message = message

    def receive(self):
        self.receive_called = True

    def close(self):
        self.connected = False


class DummyParser(object):

    def __init__(self):
        self.parse_called = False

    def parse(self):
        self.parse_called = True


class TestMessagingClient(TestCase):

    def setUp(self):
        self.socket = DummySocket()
        self.parser = DummyParser()
        self.client = MessagingClient(command_line_parser=self.parser, socket=self.socket)
        self.test_message = "Happy messaging!"

    def test_parse_command_line(self):
        self.client.parse_command_line()
        self.assertTrue(self.parser.parse_called)

    def test_set_remote_address(self):
        host = "127.0.0.1"
        port = 5000
        self.client.set_address(host, port)
        self.assertEqual(host, self.client.host)
        self.assertEqual(port, self.client.port)

    def test_enable_debug_mode(self):
        self.client.set_debug_mode(True)
        self.assertTrue(self.client.debug)

    def test_connecting(self):
        self.client.connect()
        self.assertTrue(self.socket.connected)
        self.client.close()
        self.assertFalse(self.socket.connected)

    def test_send_message(self):
        self.client.send_message(self.test_message)
        self.assertEqual(self.test_message, self.socket.sent_message)

    def test_send_message_in_debug_mode(self):
        self.client.set_debug_mode(True)
        self.client.send_message(self.test_message)
        self.assertEqual(self.test_message, self.socket.sent_message)

    def test_receive_message(self):
        self.client.receive_response()
        self.assertTrue(self.socket.receive_called)
