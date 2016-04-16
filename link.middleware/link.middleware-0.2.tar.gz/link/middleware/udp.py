# -*- coding: utf-8 -*-

from b3j0f.conf import Configurable
from link.middleware.socket import SocketMiddleware

import socket


@Configurable(paths='middleware/udp.conf')
class UDPMiddleware(SocketMiddleware):
    """
    UDP Socket middleware.
    """

    __protocols__ = ['udp']

    def new_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.host, self.port))
        return sock

    def send(self, data, host, port):
        self._send(self.conn, data, host, port)

    def _send(self, sock, data, host, port):
        sock.sendto(data, (host, port))

    def _receive(self, sock, bufsize):
        return sock.recvfrom(bufsize)
