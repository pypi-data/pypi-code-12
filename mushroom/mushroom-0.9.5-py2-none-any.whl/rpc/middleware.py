import logging
import sys
from time import time
from datetime import datetime

from .messages import Notification
from .messages import Request


logger = logging.getLogger('mushroom.rpc.middleware')


class Middleware(object):

    def process_message(self, message):
        if isinstance(message, Notification):
            return self.process_notification(message)
        if isinstance(message, Request):
            return self.process_request(message)

    def process_notification(self, request):
        pass

    def process_request(self, request):
        pass

    def process_response(self, request, response):
        pass

    def process_exception(self, request, exception):
        pass


class MiddlewareStack(object):

    def __init__(self, middlewares):
        self.middlewares = middlewares or []

    def process_message(self, message):
        for middleware in self.middlewares:
            response = middleware.process_message(message)
            if response is not None:
                return response

    def process_response(self, message, response, middlewares=None):
        middlewares = middlewares or list(reversed(self.middlewares))
        for i, middleware in enumerate(middlewares):
            try:
                response = middleware.process_response(message, response)
                if response is not None:
                    return response
            except Exception as exception:
                # Copy sys.exc_info into exception for printing the stack trace later
                exception.exc_info = sys.exc_info()
                # Let the remaining middlewares handle the error response.
                return self.process_exception(message, exception, middlewares[i+1:])

    def process_exception(self, message, exception, middlewares=None):
        middlewares = middlewares or list(reversed(self.middlewares))
        for i, middleware in enumerate(middlewares):
            try:
                mw_response = middleware.process_exception(message, exception)
                if mw_response is not None:
                    # Let the remaining middlewares handle the response.
                    later_mw_response = self.process_response(middlewares[i+1:])
                    if later_mw_response is not None:
                        return later_mw_response
                    else:
                        return mw_response
            except Exception as e:
                exception = e
                exception.exc_info = sys.exc_info()
        raise exception.exc_info[0], exception.exc_info[1], exception.exc_info[2]

    def append(self, middleware):
        self.middlewares.append(middleware)


class MiddlewareAwareRpcHandler(object):

    def __init__(self, handler, middleware):
        self.handler = handler
        self.middleware = middleware

    def __call__(self, request):
        self.middleware.process_message(request)
        try:
            response = self.handler(request)
        except Exception as e:
            e.exc_info = sys.exc_info()
            middleware_response = self.middleware.process_exception(request, e)
            if middleware_response is not None:
                return middleware_response
            raise
        else:
            middleware_response = self.middleware.process_response(request, response)
            if middleware_response is not None:
                return middleware_response
            return response


class SlowMethodLogMiddleware(Middleware):
    '''
    Default thresholds:
    (10, 'error'), (1, 'warning')
    '''

    def __init__(self, thresholds=None):
        super(SlowMethodLogMiddleware, self).__init__()
        if thresholds is None:
            self.thresholds = [(10, 'error'), (1, 'warning')]
        else:
            self.thresholds = list(thresholds)
            self.thresholds.sort(reverse=True)

    def process_message(self, request):
        request.start_time = time()

    def process_response(self, request, response):
        self.log_if_slow(request, 'Slow method "%s" returned normally after %.3fs')

    def process_exception(self, request, exception):
        self.log_if_slow(request, 'Slow method "%s" returned an error after %.3fs')

    def log_if_slow(self, request, message):
        duration = time() - request.start_time
        for threshold, log_level in self.thresholds:
            if duration > threshold:
                log_args = (message, request.method, duration)
                log_method = getattr(logger, log_level)
                log_method(*log_args)
                break


class StatisticsMiddleware(Middleware):

    def process_message(self, request):
        request.session.last_activity = datetime.now()
        request.session.message_count = getattr(request.session, 'message_count', 0) + 1
