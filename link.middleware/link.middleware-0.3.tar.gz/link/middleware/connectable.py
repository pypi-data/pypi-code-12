# -*- coding: utf-8 -*-

from b3j0f.middleware import Middleware


class ConnectableMiddleware(Middleware):
    """
    Middleware class connecting to a remote service.
    """

    def __init__(self, *args, **kwargs):
        super(ConnectableMiddleware, self).__init__(*args, **kwargs)

        self._conn = None

    def _connect(self):
        """
        Create a connection to the remote service (must be overriden).

        :returns: connection object
        """

        raise NotImplementedError()

    def _disconnect(self, conn):
        """
        Close connection (must be overriden).

        :param conn: connection object as returned by ``_connect()``
        """

        raise NotImplementedError()

    def _isconnected(self, conn):
        """
        Check if connection is alive (must be overriden).

        :param conn: connection object as returned by ``_connect()``
        :returns: True if connection is alive, False otherwise
        """

        return False

    @property
    def conn(self):
        """
        Returns internal connection (make sure the middleware is connected).
        """

        self.connect()
        return self._conn

    def isconnected(self):
        """
        Check if middleware is connected.
        """

        return self._isconnected(self._conn)

    def connect(self):
        """
        If not already connected, connect the middleware to the remote service.
        """

        if not self.isconnected():
            self._conn = self._connect()

    def disconnect(self):
        """
        If connected, disconnect the middleware.
        """

        if self.isconnected():
            self._disconnect(self._conn)
            self._conn = None
