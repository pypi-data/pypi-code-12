#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Display server"""
import time
from threading import Thread
from lcdmanager.remote.server import ReadThread


class Display(Thread):
    """Class Display"""
    def __init__(self, fps=1, render=False):
        Thread.__init__(self)
        self.render = render
        self.fps = fps
        self.work = True
        self.managers = {}
        self.read_server = None

    def add(self, manager, name):
        """adds manager"""
        self.managers[name] = manager

    def run(self):
        """starts server and refresh screen"""
        try:
            while self.work:
                start = time.time()
                for manager in self.managers:
                    if self.render:
                        self.managers[manager].render()
                    self.managers[manager].flush()

                end = time.time()
                if end - start < self.fps:
                    t_delta = end - start
                    time.sleep(max(0, self.fps - t_delta))
        finally:
            pass

    def join(self, timeout=None):
        """stop threads"""
        self.work = False
        if self.read_server is not None:
            self.read_server.join()
        Thread.join(self, timeout)

    def start_remote(self, port, ip_address):
        """starts remote server"""
        self.read_server = ReadThread(self, port, ip_address)
        self.read_server.start()

    @property
    def names(self):
        """return manager names"""
        return self.managers.keys()
