import unittest

from mushroom.rpc.middleware import Middleware, MiddlewareStack, \
        MiddlewareAwareRpcHandler
from mushroom.rpc.exceptions import RpcError
from mushroom.rpc.exceptions import RequestException
from mushroom.rpc.dispatcher import MethodDispatcher


class MockRequest(object):

    def __init__(self, method, data=None):
        self.method = method
        self.data = data


class MyError(RuntimeError):
    pass


class ErrorMiddleware(Middleware):

    def process_exception(self, message, exception):
        if isinstance(exception, MyError):
            raise RequestException(exception.message)


class CountMiddleware(Middleware):

    def __init__(self):
        self.count = 0

    def process_message(self, message):
        self.count += 1

    def process_response(self, message, response):
        self.count -= 1

    def process_exception(self, message, exception):
        self.count -= 1


class RpcMethods(object):

    def rpc_fail(self, request):
        raise MyError('Fail!')

    def rpc_count(self, request):
        return request.data.count


class MiddlewareTestCase(unittest.TestCase):

    def setUp(self):
        self.count_middleware = CountMiddleware()
        self.middlewares = MiddlewareStack([
            ErrorMiddleware(),
            self.count_middleware,
        ])
        self.rpc_handler = MiddlewareAwareRpcHandler(
                MethodDispatcher(RpcMethods()),
                self.middlewares)

    def test_error(self):
        self.assertRaises(
                RequestException,
                self.rpc_handler,
                MockRequest('fail'))
        self.assertEquals(self.count_middleware.count, 0)

    def test_count(self):
        self.assertEquals(self.rpc_handler(MockRequest('count', self.count_middleware)), 1)
        self.assertEquals(self.count_middleware.count, 0)
