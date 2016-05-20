import socket
import json
import logging


class Sender(object):

    def __init__(self, logstash='localhost:420'):
        url_parts = logstash.split(':')
        self.host = url_parts[0]
        self.port = int(url_parts[1])
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.log = logging.getLogger('tsuru-router-tailer')

    def send(self, message):
        message = bytes(
            json.dumps(message, separators=(',', ':')),
            'utf-8'
        )
        address = (self.host, self.port)
        self.sock.sendto(
            message,
            address
        )
        self.log.debug(
            "Sending: {} to: {}".format(
                message,
                address,
            )
        )
