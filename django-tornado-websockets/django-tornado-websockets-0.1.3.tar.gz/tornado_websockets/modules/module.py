from tornado_websockets.websocket import WebSocket


class Module(object):
    def __init__(self, websocket, prefix=''):
        if not isinstance(websocket, WebSocket):
            raise ValueError('`websocket` parameter should be an instance of WebSocket class')

        self.websocket = websocket
        self.prefix = prefix

    def on(self, callback):
        """
            Shortcut for :meth:`tornado_websockets.websocket.WebSocket.on` decorator, but with a specific prefix for
            each module.

            :ction or a class method.
            :type callback: Callable
            :return: ``callback`` parameter.
        """

        callback.__name__ = self.prefix + callback.__name__

        return self.websocket.on(callback)

    def emit(self, event, data=None):
        """
            Shortcut for :meth:`tornado_websockets.websocket.WebSocket.emit` method, but with a specific prefix for
            each module.
        """

        return self.websocket.emit(self.prefix + event, data)
