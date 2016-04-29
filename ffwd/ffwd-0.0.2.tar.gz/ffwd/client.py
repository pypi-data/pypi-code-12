import json
import socket

from .samples import Metric, Event


class UDPTransport:
    def __init__(self, **kw):
        self._host = kw.get('host', '127.0.0.1')
        self._port = kw.get('port', 19000)
        self._t = (self._host, self._port)
        self._s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_json(self, message):
        self._s.sendto(json.dumps(message), self._t)


class FFWD:
    def __init__(self, **kw):
        self._transport_type = kw.pop('transport', UDPTransport)
        self._sample_opts = kw.pop('sample_opts', {})
        self._t = self._transport_type(**kw)

    def metric(self, key, **tags):
        return Metric(self, key, tags, self._sample_opts)

    def event(self, key, **tags):
        return Event(self, key, tags, self._sample_opts)

    def send_json(self, message):
        self._t.send_json(message)
