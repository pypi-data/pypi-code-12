# -*- coding: utf-8 -*-
"""
    pyxs._server
    ~~~~~~~~~~~~

    This module implements a basic XenStore server for testing.

    :copyright: (c) 2016 by pyxs authors and contributors, see AUTHORS
                for more details.
    :license: LGPL, see LICENSE for more details.
"""

from gevent import monkey
monkey.patch_all()

import os
import socket

from gevent.server import StreamServer

from ._internal import NUL, Op, Packet
from .exceptions import ConnectionError
from .connection import UnixSocketConnection, _UnixSocketTransport, \
    _get_unix_socket_path


def bind_unix_listener(path, backlog=50):
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.setblocking(0)
    if os.path.exists(path):
        os.remove(path)

    sock.bind(path)
    sock.listen(backlog)
    return sock


class ClientTransport(_UnixSocketTransport):
    def __init__(self, sock):
        self.sock = sock


class ClientConnection(UnixSocketConnection):
    def __init__(self, sock):
        super(ClientConnection, self).__init__("<unknown>")

        self.transport = ClientTransport(sock)


class Server(object):
    def __init__(self, unix_socket_path=None):
        self.storage = {}
        self.handlers = dict((op, getattr(self, name.lower(), None))
                             for name, op in Op._asdict().items())

        unix_socket_path = unix_socket_path or _get_unix_socket_path()
        self.stream_server = StreamServer(
            bind_unix_listener(unix_socket_path), self)

    def __call__(self, sock, addr):
        connection = ClientConnection(sock)
        try:
            while True:
                request = connection.recv()
                print("<<<", request)
                handler = self.handlers[request.op]
                response = make_response(
                    request, handler(*request.payload.rstrip(NUL).split(NUL)))
                print(">>>", response)
                connection.send(response)
        except ConnectionError:
            pass
        finally:
            connection.close()

    def serve_forever(self):
        self.stream_server.serve_forever()

    def read(self, path):
        return b"foo" + NUL


def make_response(request, payload):
    return request._replace(size=len(payload), payload=payload)


if __name__ == "__main__":
    Server("/tmp/xsd").serve_forever()
