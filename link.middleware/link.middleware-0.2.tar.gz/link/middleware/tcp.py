# -*- coding: utf-8 -*-

from b3j0f.conf import Configurable
from link.middleware.socket import SocketMiddleware

import socket


@Configurable(paths='middleware/tcp.conf')
class TCPMiddleware(SocketMiddleware):
    """
    TCP socket middleware.
    """

    __protocols__ = ['tcp']

    def new_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        return sock

    def _send(self, sock, data):
        sock.send(data)

    def _receive(self, sock, bufsize):
        return sock.recv(bufsize)
