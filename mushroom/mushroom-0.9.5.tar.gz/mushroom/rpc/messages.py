from gevent.event import AsyncResult


class Message(object):
    '''
    Base class for all messages.
    '''

    @staticmethod
    def from_list(l):
        '''
        Parse a list as defined in the protocol into a message object.

        :param l: list to be parsed
        '''
        if not isinstance(l, (list, tuple)):
            raise ValueError('Message is not encoded as list or tuple')
        try:
            message_class = MESSAGE_CLASS_BY_CODE[l[0]]
        except KeyError:
            raise ValueError('Unsupported message code: %r' % l[0])
        message = message_class.from_list(l)
        return message


class Heartbeat(Message):
    '''
    Heartbeat message
    '''
    code = 0

    def __init__(self, last_message_id):
        '''
        Constructur for heartbeat messages

        :param last_message_id: the message id being acknowledged by this
            heartbeat message
        '''
        self.last_message_id = last_message_id

    @staticmethod
    def from_list(l):
        '''
        Parse list into a heartbeat message

        :param l: list to be parsed
        '''
        return Heartbeat(l[1])

    def to_list(self):
        '''
        Serialize this message into a list
        '''
        return [self.code, self.last_message_id]


class Notification(Message):
    '''
    Notification message
    '''
    code = 1

    def __init__(self, message_id, method, data=None):
        '''
        Constructor for notification messages

        :param method: name of the method being called
        :param data: data for the method being called
        :param message_id: id of this message
        '''
        self.message_id = message_id
        self.method = method
        self.data = data

    @staticmethod
    def from_list(l):
        '''
        Parse list into a notification message

        :param l: list to be parsed
        '''
        return Notification(*l[1:])

    def to_list(self):
        '''
        Serialize this message into a list
        '''
        return [self.code, self.message_id, self.method, self.data]


class Request(Message):
    '''
    Request message
    '''
    code = 2

    def __init__(self, message_id, method, data=None):
        '''
        Constructor for request messages

        :param method: name of the method being called
        :param data: data for the method being called
        :param message_id: id of this message
        '''
        self.message_id = message_id
        self.method = method
        self.data = data
        self._response = AsyncResult()

    def to_list(self):
        return [self.code, self.message_id, self.method, self.data]

    @staticmethod
    def from_list(l):
        '''
        Parse list into a request message

        :param l: list to be parsed
        '''
        return Request(*l[1:])

    @property
    def response(self):
        return self.get_response()

    @response.setter
    def response(self, response):
        self._response.set(response)

    def get_response(self, block=True, timeout=None):
        '''
        Get response for this request.

        :param block: block until response is available
        :type block: bool
        :param timeout: seconds to wait before raising a :class:`mushroom.rpc.RequestTimeout` error
        :type timeout: int or None
        :rtype: :class:`mushroom.rpc.Response` or :class:`mushroom.rpc.Error`
        :raises: :class:`mushroom.rpc.RequestTimeout`
        '''
        return self._response.get(block=block, timeout=timeout)


class Response(Message):
    '''
    Response message
    '''
    code = 3

    def __init__(self, message_id, request_message_id, data=None):
        '''
        Constructor for response messages

        :param request_message_id: the message id of the request which
                caused this response
        :param data: response data of the method which was called
        :param message_id: id of this message
        '''
        self.request_message_id = request_message_id
        self.message_id = message_id
        self.data = data
        self.request = None

    @staticmethod
    def for_request(message_id, request, data=None):
        '''
        Named constructor when the request is known. Some transports
        need the reference to the original request object when sending
        the reply for a request. Therefore the Engine_ generates
        all responses using this method.

        :param request: the request which caused this response
        :param data: response data of the method which was called
        :param message_id: id of this message
        '''
        response = Response(message_id, request.message_id, data)
        response.request = request
        return response

    @staticmethod
    def from_list(l):
        '''
        Parse list into a response message

        :param l: list to be parsed
        '''
        return Response(*l[1:])

    def to_list(self):
        '''
        Serialize this message into a list
        '''
        if isinstance(self.request, Request):
            return [self.code, self.message_id, self.request.message_id, self.data]
        else:
            return [self.code, self.message_id, self.request, self.data]


class Error(Message):
    '''
    Error message

    This is the message class and not the exception. The `RpcEngine`
    will raise a `RequestException` upon receiving this message type.
    '''
    code = 4

    def __init__(self, message_id, request_message_id, data=None):
        '''
        Constructor for error messages

        :param request_message_id: the message id of the request which
                caused this response
        :param data: response data of the method which was called
        :param message_id: id of this message
        '''
        self.request_message_id = request_message_id
        self.message_id = message_id
        self.data = data
        self.request = None

    @staticmethod
    def for_request(message_id, request, data=None):
        '''
        Named constructor when the request is known. Some transports
        need the reference to the original request object when sending
        the reply for a request. Therefore the `RpcEngine` generates
        all errors using this method.

        :param request: the request which caused this response
        :param data: response data of the method which was called
        :param message_id: id of this message
        '''
        error = Error(message_id, request.message_id, data)
        error.request = request
        return error

    @staticmethod
    def from_list(l):
        '''
        Parse list into a error message

        :param l: list to be parsed
        '''
        return Error(*l[1:])

    def to_list(self):
        '''
        Serialize this message into a list
        '''
        if isinstance(self.request, Request):
            return [self.code, self.message_id, self.request.message_id, self.data]
        else:
            return [self.code, self.message_id, self.request, self.data]


class Disconnect(Message):
    '''
    Disconnect message
    '''
    code = -1

    @staticmethod
    def from_list(l):
        '''
        Parse list into a disconnect message

        :param l: list to be parsed
        '''
        return Disconnect()

    def to_list(self):
        '''
        Serialize this message into a list
        '''
        return [self.code]


# Dictionary which maps the message codes to the according classes.
# This is only used by the `Message` class in the static `from_list`
# method.
MESSAGE_CLASS_BY_CODE = {
    Heartbeat.code: Heartbeat,
    Notification.code: Notification,
    Request.code: Request,
    Response.code: Response,
    Error.code: Error,
    Disconnect.code: Disconnect
}
