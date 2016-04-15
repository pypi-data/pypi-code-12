# Copyright (C) 2013 Johnny Vestergaard <jkv@unixcluster.dk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import sys

import gevent
import gevent.event
from gevent import Greenlet
from gevent.server import StreamServer

import heralding.capabilities.handlerbase
from heralding.reporting.file_logger import FileLogger
from heralding.reporting.zmq_logger import ZmqLogger

from ipify import get_ip

logger = logging.getLogger(__name__)


class Honeypot(object):
    public_ip = ''
    def __init__(self, config):
        """
        :param config: configuration dictionary.
        """
        assert config != None
        self.readyForDroppingPrivs = gevent.event.Event()
        self.config = config
        self._servers = []
        self._greenlets = []

    def _record_and_lookup_public_ip(self):
        while True:
            try:
                Honeypot.public_ip = get_ip()
                logger.warn('Found public ip: {0}'.format(Honeypot.public_ip))
            except Exception as ex:
                Honeypot.public_ip = ''
                logger.warn('Could not request public ip from ipify, error: {0}'.format(ex))
            gevent.sleep(3600)

    def start(self):
        """ Starts services. """

        if 'public_ip_as_destination_ip' in self.config and self.config['public_ip_as_destination_ip'] == True:
            self._greenlets.append(gevent.spawn(self._record_and_lookup_public_ip))

        # start activity logging
        if 'activity_logging' in self.config:
            if 'file' in self.config['activity_logging'] and self.config['activity_logging']['file']['enabled']:
                logFile = self.config['activity_logging']['file']['filename']
                FileLogger(logFile).start()
            if 'zmq' in self.config['activity_logging'] and self.config['activity_logging']['zmq']['enabled']:
                zmq_url = self.config['activity_logging']['zmq']['url']
                client_pub_key = self.config['activity_logging']['zmq']['client_public_key']
                client_secret_key = self.config['activity_logging']['zmq']['client_secret_key']
                server_pub_key = self.config['activity_logging']['zmq']['server_public_key']
                ZmqLogger(zmq_url, client_pub_key, client_secret_key, server_pub_key).start()

        for c in heralding.capabilities.handlerbase.HandlerBase.__subclasses__():

            cap_name = c.__name__.lower()
            if cap_name in self.config['capabilities']:
                if not self.config['capabilities'][cap_name]['enabled']:
                    continue
                port = self.config['capabilities'][cap_name]['port']
                # carve out the options for this specific service
                options = self.config['capabilities'][cap_name]
                # capabilities are only allowed to append to the session list
                cap = c(options)

                try:
                    # Convention: All capability names which end in 's' will be wrapped in ssl.
                    if cap_name.endswith('s'):
                        server = StreamServer(('0.0.0.0', port), cap.handle_session,
                                              keyfile=self.key, certfile=self.cert)
                    else:
                        server = StreamServer(('0.0.0.0', port), cap.handle_session)

                    logger.debug('Adding {0} capability with options: {1}'.format(cap_name, options))
                    self._servers.append(server)
                    server_greenlet = Greenlet(server.start())
                    self._greenlets.append(server_greenlet)
                except Exception as ex:
                    error_message = "Could not start {0} server on port {1}. Error: {2}".format(c.__name__, port, ex)
                    logger.error(error_message)
                    sys.exit(error_message)
                else:
                    logger.info('Started {0} capability listening on port {1}'.format(c.__name__, port))

        self.readyForDroppingPrivs.set()
        gevent.joinall(self._greenlets)

    def stop(self):
        """Stops services"""

        for s in self._servers:
            s.stop()

        for g in self._greenlets:
            g.kill()

        logger.info('All workers stopped.')

    def blokUntilReadyForDroppingPrivs(self):
        self.readyForDroppingPrivs.wait()
