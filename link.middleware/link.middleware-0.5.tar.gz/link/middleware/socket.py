# -*- coding: utf-8 -*-

from b3j0f.conf import Configurable, category
from link.middleware.connectable import ConnectableMiddleware
from link.middleware import CONF_BASE_PATH


@Configurable(
    paths='{0}/socket.conf'.format(CONF_BASE_PATH),
    conf=category('SOCKET')
)
class SocketMiddleware(ConnectableMiddleware):
    """
    Socket middleware.
    """

    def new_socket(self, host, port):
        """
        Create a new socket (must be overriden).

        :param host: host to connect to
        :type host: str
        :param port: port to connect to
        :type port: int
        :returns: socket object
        """

        raise NotImplementedError()

    def _connect(self):
        socks = [
            self.new_socket(host, port)
            for host, port in self.hosts
        ]

        return socks

    def _disconnect(self, socks):
        for sock in socks:
            sock.close()

    def _isconnected(self, socks):
        return any([sock is not None for sock in socks])

    def _send(self, sock, data):
        """
        Send data into socket (must be overriden).

        :param sock: socket as returned by ``new_socket()``
        :param data: data to send
        """

        raise NotImplementedError()

    def _receive(self, sock, bufsize):
        """
        Fetch data from socket (must be overriden).

        :param sock: socket as returned by ``new_socket()``
        :param bufsize: Size of data to fetch
        :returns: data read from socket
        """

        raise NotImplementedError()

    def send(self, data):
        """
        Send data to the middleware.

        :param data: data to send
        """

        for sock in self.conn:
            self._send(sock, data)

    def receive(self, bufsize):
        """
        Fetch data from middleware.

        :param bufsize: Size of data to fetch
        :returns: data read from middleware
        """

        data = []

        for sock in self.conn:
            data.append(self._receive(sock, bufsize))

        if len(data) == 1:
            return data[0]

        else:
            return data
