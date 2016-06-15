from websocket import create_connection as ws
from jsonrpc_requests import Server as rpc
from atexit import register as onExit
from simplejson import dumps as json
from datetime import datetime

class Client(object):

    def __init__(self):
        self._ws = ws('ws://localhost:4000/ws')
        onExit(self.close)

        self._rpc = rpc('http://localhost:4000/rpc')

    def set(self, collection, id_, properties):
        payload = json({
            'collection': collection,
            'id': id_,
            'properties': properties
        })
        return self._ws.send(payload)

    def error(self, collection, message, properties):
        return getattr(self._rpc, 'Source.ReportError')({
            'collection': collection,
            'message': message,
            'properties': properties
        })

    def close(self):
        self._ws.close()
