# -*- coding: utf-8 -*-
"""
rio.base
~~~~~~~~~

"""

from .parser import parse_dsn
from .transports.requests import RequestsTransport

class Client(object):
    """Rio Client."""

    def __init__(self, dsn=None):
        self.dsn = dsn
        self.context = parse_dsn(dsn)
        self._transport = RequestsTransport(self.context)

    @property
    def transport(self):
        """Client transport, default is requests."""
        return self._transport

    @transport.setter
    def transport(self, new_transport):
        """Set a new transport."""
        self._transport = new_transport

    def emit(self, action, payload=None, retry=0):
        """Emit action with payload.

        :param action: an action slug
        :param payload: data, default {}
        :param retry: integer, default 0.
        :return: information in form of dict.
        """
        payload = payload or {}

        if retry:
            _retry = self.transport.retry(retry)
            emit = _retry(self.transport.emit)
        else:
            emit = self.transport.emit

        return emit(action, payload)
