# -*- coding: utf-8 -*-

import logging
import os
from pyrocumulus.commands.runtornado import RunTornadoCommand
from pyrocumulus.conf import settings
import tornado
from tornado import gen
# just to connect to signals and add to scheduler
from jaobi import models  # pragma no cover
from jaobi.reports import reduced  # pragma no cover
from jaobi.myzmq import ZMQServer
from jaobi.cache import spyapp
from jaobi import utils


class StartBECommand(RunTornadoCommand):
    description = 'Command to start Jaobi\'s backend'

    user_options = [
        # --port 9876
        {'args': ('--port',),
         'kwargs': {'default': None, 'help': 'port to listen',
                    'nargs': '?'}},

        {'args': ('--spy-port',),
         'kwargs': {'default': None, 'help': 'spy port to listen',
                    'nargs': '?'}},

        {'args': ('--loglevel',),
         'kwargs': {'default': 'info', 'help': 'log level',
                    'nargs': '?'}},

        # --pidfile some/file.pid
        {'args': ('--pidfile',),
         'kwargs': {'default': None, 'help': 'stderr log file',
                    'nargs': '?'}},
        # --kill
        {'args': ('--kill',),
         'kwargs': {'default': False, 'help': 'kill jaobi be',
                    'action': 'store_true'}},

    ]

    def run(self):

        loglevel = getattr(logging, self.loglevel.upper())
        logger = logging.getLogger('jaobi')
        logger.setLevel(loglevel)

        loop = tornado.ioloop.IOLoop.instance()
        self.application = spyapp
        self.pidfile = self.pidfile or 'jaobibe.pid'
        port = 5555
        if hasattr(settings, 'ZMQSERVER_PORT'):
            port = getattr(settings, 'ZMQSERVER_PORT', 5555)

        self.port = self.port or port
        self.spy_port = self.spy_port or 9999

        if self.kill:
            return self.killtornado()

        url = 'tcp://*:%s' % port
        server = ZMQServer(url)
        server.connect()

        msg = 'starting jaobi be at {} and spy on port {}'.format(
            url, self.spy_port)
        print(msg)

        try:
            self._write_to_file(self.pidfile, str(os.getpid()))
        except PermissionError:  # pragma no cover
            print('unable to write pid %s to file %s' % (str(os.getpid()),
                                                         self.pidfile))

        @gen.coroutine
        def listen():  # pragma: no coverage
            try:
                yield self.application.listen(self.spy_port)
            except gen.BadYieldError:
                pass

        loop.run_sync(listen)

        loop.start()
