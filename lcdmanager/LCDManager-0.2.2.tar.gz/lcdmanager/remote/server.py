#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=I0011,W0231
"""server"""
from __future__ import print_function
import socket
import shlex
from threading import Thread  # pylint: disable=I0011,C0411
from future import standard_library  # pylint: disable=I0011,C0411

standard_library.install_aliases()
BUFFER_SIZE = 1024


class ListenerThread(Thread):
    """connection listener"""
    def __init__(self, conn, addr, display):
        Thread.__init__(self)
        self.client = conn
        self.addr = addr
        # self.client.settimeout(0.5)
        self.work = True
        self.display = display

    def run(self):
        """thread"""
        while self.work:
            try:
                data = self.client.recv(BUFFER_SIZE).decode("UTF-8").strip()
                if not data:
                    break
                else:
                    response = self._command(data)
                    if response:
                        self.client.send(response.encode("UTF-8"))
            except socket.timeout:
                pass

        self.client.close()

    def join(self, timeout=None):
        """stop thread"""
        self.work = False
        Thread.join(self, timeout)

    def _command(self, cmd):
        """execute command"""
        parameters = shlex.split(cmd)
        if len(parameters) == 0:
            return None
        if parameters[0] == "get":
            return self._command_get(parameters)
        elif parameters[0] == "list":
            return self._command_list(parameters)

        return "Unknown command"

    def _command_get(self, parameters):
        """returns lcd content"""
        if len(parameters) == 2 and parameters[1] in self.display.names:
            return "\n".join(self.display.managers[parameters[1]].lcd.screen)
        else:
            return "Manager not found"

    def _command_list(self, parameters):
        """returns managers name"""
        if len(parameters) == 2 and parameters[1] == 'managers':
            return ",".join(self.display.names)
        else:
            return "Error"


class ReadThread(Thread):
    """server thread"""
    def __init__(self, display, port=1301, ip='0.0.0.0'):
        Thread.__init__(self)
        self.work = True
        self.display = display
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(0.5)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((ip, port))
        self.socket.listen(3)
        self.threads = []

    def run(self):
        """start server thread"""
        try:
            while self.work:
                try:
                    client, address = self.socket.accept()
                    listener = ListenerThread(client, address, self.display)
                    listener.start()
                    self.threads.append(listener)
                except socket.timeout:
                    pass
        finally:
            self.socket.close()
        for thread in self.threads:
            thread.join()

    def join(self, timeout=None):
        """stop server and all listeners"""
        self.work = False
        self.socket.close()
        Thread.join(self, timeout)
