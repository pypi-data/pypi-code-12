#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Display server"""
from threading import Thread
import time


class Display(Thread):
    """Class Display"""
    def __init__(self, fps=1, render=False):
        Thread.__init__(self)
        self.render = render
        self.fps = fps
        self.work = True
        self.managers = {}

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
        """stop thread"""
        self.work = False
        Thread.join(self, timeout)
