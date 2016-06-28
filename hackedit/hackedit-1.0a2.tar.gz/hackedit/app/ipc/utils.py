"""
Contains some utility functions used by both the client and the server.
"""
import logging
try:
    import dill as pickle
except ImportError:
    import pickle
import struct

from PyQt5 import QtNetwork


def _logger():
    return logging.getLogger(__name__)


def pick_free_port():
    """ Picks a free port """
    srv = QtNetwork.QTcpServer()
    srv.listen()
    port = srv.serverPort()
    srv.close()
    del srv
    return port


def read_message(socket):
    """
    Reads a message using our simple protocol (payload + data)
    """
    if not hasattr(socket, 'buffer'):
        socket.buffer = b''
    if not hasattr(socket, 'payload'):
        socket.payload = None
    socket.buffer += socket.readAll()
    if socket.payload is None and len(socket.buffer) >= 8:
            payload = socket.buffer[:8]
            socket.buffer = socket.buffer[8:]
            socket.payload = struct.unpack('Q', payload)[0]
    if socket.payload is not None and len(socket.buffer) >= socket.payload:
        return pickle.loads(socket.buffer)
    return None  # message not complete, let's wait for other packets


def send_message(socket, data):
    """
    Sends a message using our rudimentary protocol.
    """

    data = pickle.dumps(data)
    payload = struct.pack('Q', len(data))
    socket.write(payload + data)


def echo(*args):
    print('function called in a subprocess with args=', args)
