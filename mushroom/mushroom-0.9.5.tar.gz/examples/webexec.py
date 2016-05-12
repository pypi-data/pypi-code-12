#!/usr/bin/env python

import example_pythonpath
from example_utils import ExampleServer, ExampleStaticFile

import gevent
from gevent import subprocess

class WebexecServer(ExampleServer):
    urls = [
        ('/', ExampleStaticFile('webexec.html')),
    ] + ExampleServer.urls

    def server_init(self):
        gevent.spawn(self.exec_subprocess)

    def exec_subprocess(self):
        proc = subprocess.Popen(['ping', 'localhost'], stdout=subprocess.PIPE)
        while True:
            line = proc.stdout.readline().rstrip()
            if line is None:
                break
            self.sessions.notify('stdout', line)


if __name__ == '__main__':
    WebexecServer.main()
