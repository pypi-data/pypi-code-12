import socket

__author__ = 'hiepsimu'


class DNSService(object):
    def get_hostname(self):
        return socket.gethostname()