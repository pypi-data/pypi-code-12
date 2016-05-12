from itertools import count
import logging

import gevent

from . import signals
from .exceptions import RpcError, RequestTimeout, RequestException, \
        MethodNotFound
from .messages import Request, Notification, Response, Error

logger = logging.getLogger('mushroom.rpc')


class Engine(object):
    '''
    Transport neutral message factory and mapper between requests and
    responses. This is the heart of all RPC handling.
    '''

    def __init__(self, transport, rpc_handler):
        # Transport for sending and receiving messages
        self.transport = transport
        # Bind transport to the engine
        assert transport.rpc_engine is None, \
                'transport already bound to another rpc engine'
        transport.rpc_engine = self
        # Handler for inbound requests and notifications
        self.rpc_handler = rpc_handler
        # Generator for outbount message ids
        self.message_id_generator = count()
        # Dictionary for mapping outbound requests to inbound responses
        self.requests = {}

    def next_message_id(self):
        '''
        Generate the next message id for outbound messages.

        Returns: the next message id
        '''
        return self.message_id_generator.next()

    def notify(self, method, data=None, **kwargs):
        '''
        Send a notification.

        :param method: name of the method to be called
        :param data: data for the method being called
        :param kwargs: transport specific arguments
        '''
        message = Notification(self.next_message_id(), method, data)
        self.send(message, **kwargs)

    def request(self, method, data=None, timeout=None, **kwargs):
        '''
        Send a request and wait for the response or timeout. If no response
        for the given method is received within `timeout` seconds a
        `RequestTimeout` exception is raised.

        :param method: name of the method to be called
        :param data: data for the method being called
        :param timeout: timeout in seconds for this request
        :param kwargs: transport specific arguments
        '''
        request = Request(self.next_message_id(), method, data)
        self.requests[request.message_id] = request
        self.send(request, **kwargs)
        try:
            response = request.get_response(timeout=timeout)
        except gevent.Timeout:
            raise RequestTimeout
        if isinstance(response, Response):
            return response.data
        elif isinstance(response, Error):
            raise RequestException(response.data)
        else:
            raise RuntimeError('Unexpected type of response: %s' % type(response))

    def send(self, message, **kwargs):
        '''
        Hand message over to the transport.

        :param message: message to be sent
        :param kwargs: transport specific arguments
        '''
        self.transport.send(message, **kwargs)

    def handle_message(self, message):
        '''
        Handle message received from the transport.

        :param message: message to be handled
        '''
        if isinstance(message, Notification):
            # Spawn worker to process the notification. The response of
            # the worker is ignored.
            @signals.message_handler
            def worker():
                try:
                    self.rpc_handler(message)
                except MethodNotFound as e:
                    logger.warning('MethodNotFound: %s' % e.message)
                except RpcError as e:
                    logger.debug(e, exc_info=True)
                except Exception as e:
                    logger.exception(e)
            gevent.spawn(worker)
        elif isinstance(message, Request):
            # Spawn worker which waits for the response of the rpc handler
            # and sends the response message.
            @signals.message_handler
            def worker():
                try:
                    response = self.rpc_handler(message)
                except MethodNotFound as e:
                    logger.warning('MethodNotFound: %s' % e.message)
                    self.send(Error.for_request(self.next_message_id(),
                        message, e.message))
                except RpcError as e:
                    logger.debug(e, exc_info=True)
                    self.send(Error.for_request(self.next_message_id(),
                        message, e.message))
                except Exception as e:
                    logger.exception(e)
                    self.send(Error.for_request(self.next_message_id(),
                        message, 'Internal server error'))
                else:
                    if not isinstance(response, Response):
                        response = Response.for_request(self.next_message_id(),
                                message, response)
                    self.send(response)
            gevent.spawn(worker)
        elif isinstance(message, (Response, Error)):
            # Find request according to response or log an error.
            try:
                message.request = self.requests.pop(message.request_message_id)
            except KeyError:
                logger.error('Response for unknown request message id: %r' %
                        message.request_message_id)
                return
            message.request.response = message
        else:
            # Heartbeats and Disconnect messages are handled by the
            # transport and are never passed to the RPC engine.
            raise RuntimeError('Unsupported message type: %s' % type(message))
