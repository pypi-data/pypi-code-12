# -*- coding: utf-8 -*-

from b3j0f.conf import Configurable, category, Parameter
from link.middleware.connectable import ConnectableMiddleware
from link.middleware import CONF_BASE_PATH


@Configurable(
    paths='{0}/socket.conf'.format(CONF_BASE_PATH),
    conf=category(
        'SOCKET',
        Parameter(name='host', value='localhost'),
        Parameter(name='port', ptype=int, value=8000)
    )
)
class SocketMiddleware(ConnectableMiddleware):
    """
    Socket middleware.
    """

    def new_socket(self):
        """
        Create a new socket (must be overriden).

        :returns: socket object
        """

        raise NotImplementedError()

    def _connect(self):
        return self.new_socket()

    def _disconnect(self, conn):
        conn.close()

    def _isconnected(self, conn):
        return conn is not None

    def _send(self, conn, data):
        """
        Send data into socket (must be overriden).

        :param conn: socket as returned by ``new_socket()``
        :param data: data to send
        """

        raise NotImplementedError()

    def _receive(self, conn, bufsize):
        """
        Fetch data from socket (must be overriden).

        :param conn: socket as returned by ``new_socket()``
        :param bufsize: Size of data to fetch
        :returns: data read from socket
        """

        raise NotImplementedError()

    def send(self, data):
        """
        Send data to the middleware.

        :param data: data to send
        """

        self._send(self.conn, data)

    def receive(self, bufsize):
        """
        Fetch data from middleware.

        :param bufsize: Size of data to fetch
        :returns: data read from middleware
        """

        return self._receive(self.conn, bufsize)
