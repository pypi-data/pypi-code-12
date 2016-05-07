#!/usr/bin/python
# -*- coding: utf-8 -*-
#pylint: disable=I0011,W0231

"""Game event catcher"""
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
__author__ = 'Bartosz Kościów'

import socket
from threading import Thread

TCP_IP = '0.0.0.0'
TCP_PORT = 5005
BUFFER_SIZE = 1024


class ListenerThread(Thread):
    """connection listener"""
    def __init__(self, conn, addr, queue):
        Thread.__init__(self)
        self.client = conn
        self.addr = addr
        self.client.settimeout(0.5)
        self.work = True
        self.queue = queue

    def run(self):
        """thread"""
        while self.work:
            try:
                data = self.client.recv(BUFFER_SIZE).decode("UTF-8")
                if not data:
                    break
                else:
                    self.queue.put(data)
            except socket.timeout:
                pass

        self.client.close()

    def join(self, timeout=None):
        """stop thread"""
        self.work = False
        Thread.join(self, timeout)


class EventServerThread(Thread):
    """server thread"""
    def __init__(self, queue):
        Thread.__init__(self)
        self.work = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(0.5)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((TCP_IP, TCP_PORT))
        self.socket.listen(3)
        self.threads = []
        self.queue = queue

    def run(self):
        """start server thread"""
        try:
            print("Server is listening for connections...")
            while self.work:
                try:
                    client, address = self.socket.accept()
                    listener = ListenerThread(client, address, self.queue)
                    listener.start()
                    self.threads.append(listener)
                except socket.timeout:
                    pass
        finally:
            self.socket.close()
        for thread in self.threads:
            thread.join()
        print("Server down")

    def join(self, timeout=None):
        """stop server and all listeners"""
        self.work = False
        Thread.join(self, timeout)
