"""
This module implements remote procedure calls (RPC) on top of request-reply
channels (see :mod:`aiomas.channel`).

RPC connections are represented by instances of :class:`RpcClient` (one for
each side of a :class:`aiomas.channel.Channel`).  They provide access to the
functions served by the peer via :class:`Proxy` instances.  Optionally, they
can provide their own RPC service so that the peer can make calls as well.

An RPC service is an object with a ``router`` attribute which is an instance of
:class:`Router`.  A router resolves paths requested by the peer.  It can also
handle sub-routers (which allows you to build hierarchies for nested calls) and
is able to perform a reverse-lookup of a router (mapping a fuction to its
path).

Routers an be attached to both, classes and dictionaries with functions.
Dictionaires need to be wrapped with a :class:`ServiceDict`.  Classes need to
have a :class:`Service` class attribute named ``router``.  :class:`Service` is
a descriptor which creates a :class:`Router` for every instance of that class.

Functions that should be callable from the remote side must be decorated with
:func:`expose()`; :func:`Router.expose()` and :func:`Service.expose()` are
aliases for it.

"""
from asyncio import coroutine
import asyncio
import logging
import weakref

from . import channel, exceptions

__all__ = [
    'open_connection', 'start_server', 'rpc_service_process', 'expose',
    '_handle_request',
    'Service', 'ServiceDict', 'Router', 'RpcClient', 'Proxy',
]


logger = logging.getLogger(__name__)


@coroutine
def open_connection(addr, *, rpc_service=None, **kwds):
    """Return an :class:`RpcClient` connected to *addr*.

    This is a convenience wrapper for :meth:`aiomas.channel.open_connection()`.
    All keyword arguments *(kwds)* are forwared to it.

    You can optionally pass a *rpc_service* to allow the peer to call back to
    us.

    This function is a `coroutine
    <https://docs.python.org/3/library/asyncio-task.html#coroutine>`_.

    """
    if rpc_service is not None and not _is_rpc_service(rpc_service):
        raise ValueError('"%s" is not a valid RPC service.' % rpc_service)

    c = yield from channel.open_connection(addr, **kwds)
    return RpcClient(c, rpc_service)


@coroutine
def start_server(addr, rpc_service, client_connected_cb=None, **kwds):
    """Start a server socket on *host:port* and create an RPC service with
    the provided *handler* for each new client.

    This is a convenience wrapper for :meth:`aiomas.channel.start_server()`.
    All keyword arguments *(kwds)* are forwared to it.

    *rpc_service* must be an RPC service (an object with a ``router`` attribute
    that is an instance of :class:`Router`).

    *client_connected_cb* is an optional callback that will be called with
    with the :class:`RpcClient` instance for each new connection.

    Raise a :exc:`ValueError` if *handler* is not decorated properly.

    This function is a `coroutine
    <https://docs.python.org/3/library/asyncio-task.html#coroutine>`_.

    """
    if not _is_rpc_service(rpc_service):
        raise ValueError('"%s" is not a valid RPC service.' % rpc_service)

    def fac(channel):
        """Create an RPC client for each new connection and call the
        *client_connected_cb* if there is one."""
        rpc_cli = RpcClient(channel, rpc_service)
        if client_connected_cb:
            client_connected_cb(rpc_cli)
        return rpc_cli

    server = yield from channel.start_server(addr, fac, **kwds)
    return server


@coroutine
def rpc_service_process(rpc_client, router, channel):
    """RPC service process for a connection *rpc_lient*.

    Serves the functions provided by the :class:`Router` *router* via the
    :class:`~aiomas.channel.Channel` *channel*.

    Forward errors raised by the handler to the caller.

    Stop running when the connection closes.

    This function is a `coroutine
    <https://docs.python.org/3/library/asyncio-task.html#coroutine>`_.

    """
    loop = channel._loop

    try:
        while True:
            # Wait for a request
            request = yield from channel.recv()

            # Dispatch handling of the request to a sub task to make dead-locks
            # less likely when multiple agents share the same connection.
            asyncio.async(_handle_request(request, loop, router), loop=loop)

    except asyncio.CancelledError:
        pass

    except ConnectionError as ce:
        rpc_client._connection_reset(ce)

    finally:
        try:
            yield from channel.close()
        except RuntimeError:
            # May happen when the loop is already closed
            pass


@coroutine
def _handle_request(request, loop, router):
    """Handle the *request*.

    Resolve the path, execute the corresponding message and set the result
    or exception.

    """
    path, args, kwargs = request.content
    # logger.debug('Request: [%s, %s, %s]' % (path, args, kwargs))

    # Resolve requested path
    try:
        func = router.resolve(path)
    except LookupError as exc:
        yield from request.fail(exc)
        return

    # Call requested function
    try:
        res = func(*args, **kwargs)
        if asyncio.iscoroutine(res):
            res = yield from asyncio.async(res, loop=loop)
        reply = request.reply
    except Exception as e:
        reply = request.fail
        res = e

    try:
        yield from reply(res)
    except ConnectionResetError:
        pass


def _is_rpc_service(obj):
    if not hasattr(obj, 'router'):
        return False

    if not isinstance(obj.router, Router):
        return False

    return True


def expose(func):
    """Decorator that enables RPC access to the decorated function.

    *func* will not be wrapped but only gain an ``__rpc__`` attribute.

    """
    if not hasattr(func, '__call__'):
        raise ValueError('"%s" is not callable.' % func)

    func.__rpc__ = True
    return func


class ServiceDict:
    """Wrapper for dicts so that they can be used as RPC routers."""
    __rpc__ = True

    def __init__(self, dict=None):
        self.dict = {} if dict is None else dict
        """The wrapped dict."""

        self.router = Router(self)
        """The dict's router instance."""

        self.__getrpc__ = self.dict.__getitem__
        for key, val in self.dict.items():
            # Iterate over all entries and look for objects with routers.
            # Set *router* as parent to these sub-routers.
            if hasattr(val, 'router'):
                Router.set_sub_router(self.router, val.router, key)


class Service:
    """A Data Descriptor that creates a new :class:`Router` instance for each
    class instance to which it is set.

    The attribute name for the Service should always be *router*::

        class Spam:
            router = aiomas.rpc.Service()

    You can optionally pass a list with the attribute names of classes with
    sub-routers.  This required to build hierarchies of routers, e.g.::

        class Eggs:
            router = aiomas.rpc.Service()


        class Spam:
            router = aiomas.rpc.Service(['eggs'])

            def __init__(self):
                self.eggs = Eggs()  # Instance with a sub-router

    """
    def __init__(self, sub_routers=()):
        self._sub_router_names = sub_routers

    def __set__(self, instance, value):
        """Raise :exc:`AttributeError` to forbid overwriting this attribute."""
        raise AttributeError('Read-only attribute.')

    def __get__(self, instance, cls):
        """If accessed from the class, return this Service instance.  If
        accessed from an *instance*, return the :class:`Router` instance for
        *instance*.

        """
        if instance is None:
            return self

        if 'router' not in instance.__dict__:
            # Create new Router for "instance" and add all sub-router:
            router = instance.__dict__.setdefault('router', Router(instance))
            for name in self._sub_router_names:
                router.add(name)

        return instance.__dict__['router']

    expose = staticmethod(expose)
    """Alias for :func:`expose()`."""


class Router:
    """The Router resolves paths to functions provided by their object *obj*
    (or its children).  It can also perform a reverse lookup to get the path
    of the router (and the router's *obj*).

    The *obj* can be a class, an instance or a dict.

    """
    def __init__(self, obj):
        # Mark *obj* as node in the RPC hierarchy and and create an alias
        # for accessing its child elements.
        obj.__rpc__ = True
        obj.__getrpc__ = obj.__getattribute__

        self.obj = obj  #: The object to which this router belongs to.
        self.name = ''  #: The name of the router (empty for root routers).
        self.parent = None  #: The parent router or ``None`` for root routers.

        self._cache = {}  # Maps already resolved paths to functions

    @property
    def path(self):
        """The path to this router (without trailing slash)."""
        router = self
        parts = []
        while router.parent is not None:
            # We go from child to root here
            parts.append(router.name)
            router = router.parent

        return '/'.join(reversed(parts))  # Reverse to get root first

    def resolve(self, path):
        """Resolve *path* and return the corresponding function.

        *path* is a string with path components separated by */* (without
        trailing slash).

        Raise a :exc:`LookupError` if no handler function can be found for
        *path* or if the function is not exposed (see :func:`expose()`).

        """
        try:
            obj = self._cache[path]
        except KeyError:
            parent = None
            obj = self.obj
            parts = path.split('/')
            for i, name in enumerate(parts):
                try:
                    parent, obj = obj, obj.__getrpc__(name)
                except (AttributeError, KeyError):
                    raise LookupError('Name "%s" not found in "%s"' %
                                      (name, '/'.join(parts[:i]))) from None

                if not hasattr(obj, '__rpc__'):
                    cls = parent.__class__
                    raise LookupError('"%s.%s.%s" is not exposed' %
                                      (cls.__module__, cls.__qualname__, name))

            self._cache[path] = obj

        return obj

    expose = staticmethod(expose)
    """Alias for :func:`expose()`."""

    def add(self, name):
        """Add the sub-router *name* (stored at ``self.obj.<name>``) to this
        router.

        Convenience wrapper for :meth:`set_sub_router`.

        """
        router = getattr(self.obj, name).router
        self.set_sub_router(router, name)

    def set_sub_router(self, router, name):
        """Set *self* as parent for the *router* named *name*."""
        if type(router) is not Router:
            raise ValueError('"%s" is not a valid router.' % router)
        if router.parent is not None:
            raise ValueError('"%s" is already a sub service of "%s"' %
                             (router.obj, router.parent.obj))
        router.name = name
        router.parent = self


class RpcClient:
    """The RpcClient provides proxy objects for remote calls via its
    :attr:`remote` attribute.

    *channel* is a :class:`~aiomas.channel.Channel` instance for communicating
    with the remote side.

    If *rpc_service* is not ``None``, it will also start its own RPC service so
    the peer can call the functions we provide.

    """
    def __init__(self, channel, rpc_service=None):
        self.__channel = channel
        self.__channel.codec.add_serializer(object, self._serialize_obj,
                                            self._deserialize_obj)
        self.__root_router = None
        self.__service = None
        self.__connection_reset_callback = None

        if rpc_service is not None:
            self.__root_router = rpc_service.router
            self.__service = asyncio.async(
                rpc_service_process(self, rpc_service.router, channel),
                loop=channel._loop)

    @property
    def channel(self):
        """The communication :class:`~aiomas.channel.Channel` of this instance.
        """
        return self.__channel

    @property
    def service(self):
        """The RPC service process for this connection."""
        return self.__service

    @property
    def remote(self):
        """A :class:`Proxy` for remote methods."""
        return Proxy(self.__channel, '')

    def on_connection_reset(self, callback):
        """Add a *callback* that gets called if the peer closes the connection
        and thus causing the :attr:`service` process to abort.

        *callback* is a callable with a single argument, the exception that the
        :attr:`service` process raises if the connection is reset by the peer.

        If this method is called multiple times, override the current callback
        with the new one.  If *callback* is ``None``, delete the current
        callback.

        Raise a :exc:`ValueError` if *callback* is neither callable nor
        ``None``.

        Raise a :exc:`RuntimeError` if this instance has not service task
        running.

        """
        if self.__service is None:
            raise RuntimeError('This %s instance has no RPC service running.' %
                               self.__class__.__name__)

        if not (callback is None or hasattr(callback, '__call__')):
            raise ValueError('%r must be "None" or callable but is neither' %
                             callback)

        self.__connection_reset_callback = callback

    @coroutine
    def close(self):
        """`Coroutine
        <https://docs.python.org/3/library/asyncio-task.html#coroutine>`_ that
        closes the connection and waits for all sub tasks to finish."""
        self.close()
        yield from self.__channel.close()
        if self.__service is not None:
            if not self.__service.done():
                self.__service.cancel()
            yield from self.__service

    def _connection_reset(self, exc):
        """Callback that is executed when a :exc:`ConnectionError` is raised
        within :attr:`service`.

        Using the *connection reset callback* (also see
        :meth:`on_connection_reset()`), the user can check if the connection
        reset was intentional or an error and react accordingly.

        """
        if self.__connection_reset_callback is not None:
            self.__connection_reset_callback(exc)

    def _serialize_obj(self, obj):
        """Fallback serializer for all objects for which no other serializer
        was found.

        It will only serialize valid RPC services and only if "self" has a
        service process running and the RPC service is associated with it.

        Else, raise a :exc:`SerializationError`.

        """
        # Check if "obj" is a valid RPC service

        if not _is_rpc_service(obj):
            raise exceptions.SerializationError('No serializer found for type '
                                                '"%s"' % type(obj))

        # Check if we have a service running:
        if self.__root_router is None:
            raise exceptions.SerializationError(
                'No RPC service running for this side of the connection.  '
                'Cannot send serice proxy.')

        # Check if "obj.router" is self.__root_router or one of its children
        router = obj.router
        while router.parent is not None:
            router = router.parent
        if router is not self.__root_router:
            raise exceptions.SerializationError('The RPC service "%r" is not '
                                                'exposed for this connection' %
                                                obj)

        return obj.router.path

    def _deserialize_obj(self, path):
        return Proxy(self.__channel, path)


class Proxy:
    """Proxy object for remote objects and functions."""
    def __init__(self, channel, path):
        self._channel = channel
        self._path = path
        self._cache = weakref.WeakValueDictionary()
        self._str = None

    def __repr__(self):
        return '<%s.%s at 0x%x>' % (self.__module__, self, id(self))

    def __str__(self):
        return self._str if self._str else '%s(%r, %r)' % (
            self.__class__.__name__,
            self._channel.get_extra_info('peername')[:2],
            self._path)

    def __getattr__(self, name):
        """Return a new proxy for *name*."""
        if name in self._cache:
            proxy = self._cache[name]
        else:
            path = name if not self._path else self._path + '/' + name
            proxy = self.__class__(self._channel, path)
            self._cache[name] = proxy

        return proxy

    def __call__(self, *args, **kwargs):
        """Call the remote method represented by this proxy and return its
        result.

        The result is a future, so you need to ``yield from`` it in order to
        get the actual return value (or exception).

        """
        if not self._path:
            raise AttributeError('No RPC function name specified.')
        return self._channel.send((self._path, args, kwargs))

    def __eq__(self, other):
        return self._channel is other._channel and self._path == other._path

    def __hash__(self):
        return hash(self._channel) + hash(self._path)
