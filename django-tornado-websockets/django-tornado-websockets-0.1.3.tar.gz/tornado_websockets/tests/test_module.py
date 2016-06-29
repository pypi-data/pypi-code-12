from tornado.concurrent import Future
from tornado.testing import gen_test
from tornado.web import Application

from tornado_websockets.modules.module import Module
from tornado_websockets.tests.helpers import WebSocketBaseTestCase, TestWebSocketHandler
from tornado_websockets.websocket import WebSocket


class MyModule(Module):
    def __init__(self, websocket, prefix='my_module_'):
        Module.__init__(self, websocket, prefix)


class TestMyModule(WebSocketBaseTestCase):
    def get_app(self):
        self.close_future = Future()

        self.websocket = WebSocket('my_module', add_to_handlers=False)
        self.app_my_module = MyModule(self.websocket)

        return Application([
            ('/ws/my_module', TestWebSocketHandler, {
                'websocket': self.websocket,
                'close_future': self.close_future
            }),
        ])

    @gen_test
    def test_method_on_with_prefix(self):
        @self.app_my_module.on
        def first_event(socket, data):
            socket.emit('response', 'first_event')

        self.assertTrue(callable(self.app_my_module.websocket.events.get('my_module_first_event')))

    @gen_test
    def test_method_on_without_prefix(self):
        @self.app_my_module.websocket.on
        def second_event(socket, data):
            socket.emit('response', 'second_event')

        self.assertTrue(callable(self.app_my_module.websocket.events.get('second_event')))
