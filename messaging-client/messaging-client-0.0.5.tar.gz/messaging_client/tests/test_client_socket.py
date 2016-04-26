from unittest import TestCase
import unittest.mock as mock
from messaging_client.client_socket import ClientSocket


class TestClientSocket(TestCase):

    @mock.patch('messaging_client.client_socket.socket')
    def test_connecting(self, mock_socket):
        client = ClientSocket()
        client.connect('0.0.0.0', 5000)
        client.socket.connect.assert_called_with(('0.0.0.0', 5000))
        client.close()
        client.socket.close.assert_called_with()

    @mock.patch('messaging_client.client_socket.socket')
    def test_send_message(self, mock_socket):
        client = ClientSocket()
        client.connect('0.0.0.0', 5000)
        client.socket.connect.assert_called_with(('0.0.0.0', 5000))
        message = "Happy messaging!"
        byte_message = str.encode(message)
        client.send(message)
        client.socket.send.assert_called_with(byte_message)

