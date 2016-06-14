# -*- coding: utf-8 -*-

import socket
from netkit.stream import Stream


class TcpClient(object):
    """
    封装过的tcp client
    """

    box_class = None
    address = None
    timeout = None
    stream = None

    def __init__(self, box_class, host=None, port=None, timeout=None, address=None):
        """
        :param box_class:
        :param host:
        :param port:
        :param timeout:
        :param address: 优先级比host,port 更高。如果传入 list/tuple 代表是网络ip和端口；如果传入str，则代表是unix文件
        :return:
        """
        self.box_class = box_class
        self.address = (host, port)

        if address is not None:
            self.address = address

        self.timeout = timeout

    def connect(self):
        """
        连接服务器，失败会抛出异常
        :return:
        """
        if isinstance(self.address, (list, tuple)):
            socket_type = socket.AF_INET
        elif isinstance(self.address, (str, unicode)):
            socket_type = socket.AF_UNIX
        else:
            raise Exception('invalid address: %s' % self.address)

        sock = socket.socket(socket_type, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        try:
            sock.connect(self.address)
        except Exception, e:
            sock.close()
            raise e

        self.stream = Stream(sock)

    def read(self):
        """
        如果超时会抛出异常 socket.timeout
        :return:
        """
        if self.closed():
            return None

        box = self.box_class()

        data = self.stream.read_with_checker(box.unpack)
        if not data:
            return None

        return box

    def write(self, data):
        """
        写入
        :param data:
        :return:    True/False
        """
        if self.closed():
            return False

        if isinstance(data, self.box_class):
            data = data.pack()
        elif isinstance(data, dict):
            data = self.box_class(data).pack()

        return self.stream.write(data)

    def close(self):
        if not self.stream:
            return

        return self.stream.close()

    def closed(self):
        if not self.stream:
            return True

        return self.stream.closed()

    def __str__(self):
        return 'box_class: %s, address: %s, timeout: %s' % (self.box_class, self.address, self.timeout)
