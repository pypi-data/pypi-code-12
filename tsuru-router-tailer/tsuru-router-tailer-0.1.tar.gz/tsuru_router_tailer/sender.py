import socket
import json


class Sender(object):

    def __init__(self, logstash='localhost:420'):
        url_parts = logstash.split(':')
        self.host = url_parts[0]
        self.port = int(url_parts[1])
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, message):
        self.sock.sendto(
            bytes(
                json.dumps(message, separators=(',', ':')),
                'utf-8'
            ),
            (self.host, self.port)
        )
