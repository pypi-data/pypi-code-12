from .exceptions import MethodNotFound


class MethodDispatcher(object):
    '''
    Dispatcher implementation that calls methods on an object with a
    specific prefix and/or suffix. This makes it possible to define
    objects that provides a set of methods which can then be called by
    the client.

    Note: Using an empty prefix, ``_`` or ``__`` is highly discouraged as
    it allows the client to call methods like methods like ``__del__``.
    The same holds true for the suffix. If you really want to dispatch
    methods without a prefix or suffix it is a good idea to write a
    custom dispatcher that implements some checks for this.
    '''

    def __init__(self, obj, prefix='rpc_', suffix=''):
        '''
        Constructor for the method dispatcher.

        :param obj: object instance which is used for the method lookup
        :param prefix: string prefix which is prepended to the method name
            when looking up the method
        :param suffix: string suffix which is appended to the method name
            when looking up the method
        '''
        self.obj = obj
        self.prefix = prefix
        self.suffix = suffix

    def __call__(self, request):
        '''
        The `Engine` calls the request handler like it was a function
        that takes the request as sole argument and returns the response.
        This function implements the adapter for this interface and makes
        it possible to use this class as `handler` for the `Engine`.

        :param request: request object
        '''
        method_name = self.prefix + request.method + self.suffix
        try:
            method = getattr(self.obj, method_name)
        except AttributeError:
            raise MethodNotFound(method_name)
        return method(request)


def dummy_rpc_handler(request):
    '''
    Dummy RPC handler that raises a MethodNotFound exception for
    all calls. This is useful for applications that do not need do
    receive any data from the client but only publish data.
    '''
    raise MethodNotFound(request.method)
