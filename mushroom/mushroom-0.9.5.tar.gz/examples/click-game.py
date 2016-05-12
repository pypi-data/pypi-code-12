#!/usr/bin/env python

from time import time
from random import random

import gevent

import example_pythonpath
from example_utils import ExampleServer, ExampleStaticFile


class TimePusherServer(ExampleServer):
    urls = [
        ('/', ExampleStaticFile('click-game.html')),
    ] + ExampleServer.urls

    def server_init(self):
        self.score = 0
        gevent.spawn(self.main_loop)

    def main_loop(self):
        while True:
            gevent.sleep(2)
            x = random()
            y = random()
            self.sessions.notify('target', { 'x': x, 'y': y })

    def rpc_click(self, request):
        self.score += 1
        self.sessions.notify('score', self.score)


if __name__ == '__main__':
    TimePusherServer.main()
