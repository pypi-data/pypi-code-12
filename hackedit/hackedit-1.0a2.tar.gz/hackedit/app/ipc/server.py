"""
This module contains the server script that will execute the requested function
and send back the results.
"""
import logging
import os
import socket
import struct
import sys
import traceback

from PyQt5.QtCore import QCoreApplication


try:
    import dill as pickle
except ImportError:
    import pickle


def read_bytes(conn, size):
    """
    Read x bytes

    :param size: number of bytes to read.

    """
    data = bytes()
    while len(data) < size:
        tmp = conn.recv(size - len(data))
        data += tmp
        if tmp == '':
            raise RuntimeError("socket connection broken")
    return data


def recv(conn, size):
    data = b''
    while len(data) < size:
        data += conn.recv(size - len(data))
        # print('read %d/%d bytes' % (len(data), size))
    return data


def get_msg_len(conn):
    """ Gets message len """
    payload = struct.unpack('Q', recv(conn, 8))
    return payload[0]


def read(conn):
    """ Reads a json string from socket and load it. """
    size = get_msg_len(conn)
    return pickle.loads(recv(conn, size))


def send(conn, obj):
    """
    Send the python object obj. Obj must be pickable.
    """
    msg = pickle.dumps(obj)
    header = struct.pack('Q', len(msg))
    conn.sendall(header)
    conn.sendall(msg)
    del msg


def handle(conn):
    """
    Handles a work request.
    """
    data = read(conn)
    fct = data['function']
    args = data['arguments']
    try:
        print('running function <%s>' % fct)
        ret_val = fct(*args)
    except Exception as e:
        tb = traceback.format_exc()
        print('function error: ', tb)
        send(conn, {'exception': e, 'traceback': tb})
    else:
        print('function finished, sending result')
        send(conn, {'ret_val': ret_val})
    finally:
        conn.close()


if __name__ == '__main__':
    class Unbuffered(object):
        def __init__(self, stream):
            self.stream = stream

        def write(self, data):
            self.stream.write(data)
            self.stream.flush()

        def __getattr__(self, attr):
            return getattr(self.stream, attr)

    logging.basicConfig(format='%(levelname)s:%(name)s:%(message)s',
                        level=logging.DEBUG)

    QCoreApplication.setOrganizationName('HackEdit')
    QCoreApplication.setOrganizationDomain('hackedit.com')
    QCoreApplication.setApplicationName('HackEdit')

    sys.path.insert(0, os.environ['HACKEDIT_VENDOR_PATH'])

    sys.stdout = Unbuffered(sys.stdout)

    host = ''
    port = int(sys.argv[1])
    srv = socket.socket()
    # bind socket to local host and port
    try:
        srv.bind((host, port))
    except Exception as e:
        print('Failed to bind socket. Error code: %s' % str(e))
        sys.exit(1)
    srv.listen(1)
    print('server is listening on localhost:%s' % port)
    # wait for the client to connect and handle the request
    conn, addr = srv.accept()
    handle(conn)
