"""
This module implements the base class for agents (:class:`Agent`) and
containers for agents (:class:`Container`).

Every agent must live in a container.  A container can contain one ore more
agents.  Containers are responsible for making connections to other containers
and agents.  They also provide a factory function for spawning new agent
instances and registering them with the container.

Thus, the :class:`Agent` base class is very light-weight.  It only has a name,
a reference to its container and an RPC router (see :mod:`aiomas.rpc`).

"""
import asyncio
import collections
import weakref
import socket
import ssl as sslmod

from . import channel, clocks, local_queue, rpc, util

__all__ = ['SSLCerts', 'Container', 'Agent']


PROTOCOLS = {
    'tcp',  # TCP sockets
    'ipc',  # Inter Process Communication with Unix domain sockets
    'local',  # LocalQueue transport
}


SSLCerts = collections.namedtuple('SSLCerts', 'cafile, certfile, keyfile')
""":func:`~collections.namedtuple` storing the names of a CA file, a
certificate file and the associated private key file.

See also :func:`aiomas.util.make_ssl_server_context()` and
:func:`aiomas.util.make_ssl_client_context()`.

"""


def _get_base_url(addr):
    # Get base URL for agents (tcp or ipc)
    if type(addr) is tuple:
        host, port = addr
        if host in [None, '', '::', '0.0.0.0']:
            host = socket.getfqdn()
        base_url = '%s://%s:%s/' % ('tcp', host, port)
    elif isinstance(addr, local_queue.LocalQueue):
        base_url = 'local://%s/' % addr.queue_id
    else:
        base_url = '%s://[%s]/' % ('ipc', addr)

    return base_url


def _make_ssl_contexts(ssl):
    """Derive and return a tuple *(Server SSLContext, Client SSLContext)* from
    *ssl*.

    *ssl* may either be a :class:`SSLCerts` instance or a tuple of two
    :class:`ssl.SSLContext` instances.

    In other cases, return ``(None, None)``.

    """
    if type(ssl) is SSLCerts:
        ssl_server_ctx = util.make_ssl_server_context(**ssl._asdict())
        ssl_client_ctx = util.make_ssl_client_context(**ssl._asdict())
    elif type(ssl) is tuple:
        if (len(ssl) != 2 or
                type(ssl[0]) is not sslmod.SSLContext or
                type(ssl[1]) is not sslmod.SSLContext):
            raise TypeError('"ssl" must contain two "ssl.SSLContext" '
                            'instances; one for the server and one for '
                            'the client.')
        ssl_server_ctx = ssl[0]
        ssl_client_ctx = ssl[1]
    else:
        ssl_server_ctx = None
        ssl_client_ctx = None

    return ssl_server_ctx, ssl_client_ctx


class Container:
    """Container for agents.

    You should not instantiate containers directly but use the :meth:`create()`
    method/coroutine instead.  This makes sure that the container's server
    socket is fully operational when it is created.

    The container allows its agents to create connections to other agents (via
    :meth:`connect()`).

    In order to destroy a container and close all of its sockets, call
    :meth:`shutdown()`.

    """
    router = rpc.Service(['agents'])

    @classmethod
    def create(cls, addr, *, clock=None, codec=None, extra_serializers=None,
               ssl=None, as_coro=False):
        """Instantiate a container and create a server socket for it.

        This function is a classmethod and `coroutine
        <https://docs.python.org/3/library/asyncio-task.html#coroutine>`_.

        :param addr:
            is the address that the server socket is bound to.  It may be
            a ``(host, port)`` tuple for a TCP socket, a path for a Unix domain
            socket, or a *LocalQueue* instance as returned by the
            :func:`aiomas.local_queue.get_queue()` function.

            **TCP sockets**

            If ``host`` is ``'0.0.0.0'`` or ``'::'``, the server is bound to
            all available IPv4 *or* IPv6 interfaces respectively.  If ``host``
            is ``None`` or ``''``, the server is bound to all available IPv4
            *and* IPv6 interfaces.  In these cases, the machine's FQDN (see
            :func:`socket.getfqdn()`) should be resolvable and point to that
            machine as it will be used for the agent's addresses.

            If ``host`` is a simple (IPv4 or IPv6) IP address, it will be used
            for the agent's addresses as is.

            **LocalQueue**

            In contrast to TCP, multiple LocalQueue connections between
            containers (within the same thread and OS process) send and receive
            message in a deterministic order, which is useful for testing and
            debugging.

            LocalQueue instances should be retrieved via the
            :func:`aiomas.local_queue.get_queue()` function (which also
            available as ``aiomas.get_queue()``). This function always
            returns the same instance for a given queue ID.

        :param clock:
            can be an instance of :class:`~aiomas.clocks.BaseClock`.

            It allows you to decouple the container's (and thus, its agent's)
            time from the system clock.  This makes it easier to integrate your
            system with other simulators that may provide a clock for you or to
            let your MAS run as fast as possible.

            By default, the real-time :class:`~aiomas.clocks.AsyncioClock` will
            be used.

        :param codec:
            can be a :class:`~aiomas.codecs.Codec` subclass (not an instance!).
            :class:`~aiomas.codecs.JSON` is used by default.

        :param extra_serializers:
            is an optional list of extra serializers for the codec.  The list
            entries need to be callables that return a tuple with the arguments
            for :meth:`~aiomas.codecs.Codec.add_serializer()`.

        :param ssl:
            allows you to enable TLS for all incoming and outgoing TCP
            connections.  It may either be an :class:`SSLCerts` instance or
            a tuple containing two :class:`~ssl.SSLContext` instances, where
            the first one will be used for the server socket, the second one
            for client sockets.

        :param as_coro:
            must be set to ``True`` if the event loop is already running when
            you call this method.  This function then returns a coroutine that
            you need to ``await`` in order to get the container.  By default it
            will block until the server has been started and return the
            container.

        :return:
            a fully initialized :class:`Container` instance if *async* is
            ``False`` or else a coroutine returning the instance when it is
            done.

        Invocation examples::

            # Synchronous:
            container = Container.create(...)

            # Asynchronous:
            container = await Container.create(..., as_coro=True)


        """
        base_url = _get_base_url(addr)
        ssl_server_ctx, ssl_client_ctx = _make_ssl_contexts(ssl)

        # Get default codec and clock if none were provided
        if codec is None:
            codec = channel.DEFAULT_CODEC
        if clock is None:
            clock = clocks.AsyncioClock()

        # Prepend the Arrow date serializer to the list of serializers
        if extra_serializers is None:
            extra_serializers = []
        extra_serializers = [util.arrow_serializer] + extra_serializers

        # Additional keyword arguments for connecting to other containers
        connect_kwargs = {
            'codec': codec,
            'extra_serializers': extra_serializers,
            'ssl': ssl_client_ctx,
        }

        # Actually instantiate the container and start the server socket
        @asyncio.coroutine
        def _start():
            container = cls(base_url, clock, connect_kwargs)
            tcp_server = yield from rpc.start_server(
                addr,
                container,
                client_connected_cb=container._add_to_con_cache,
                codec=codec,
                extra_serializers=extra_serializers,
                ssl=ssl_server_ctx)
            container.set_server(tcp_server)
            return container

        if as_coro:
            return _start()
        else:
            return util.run(_start())

    def __init__(self, base_url, clock, connect_kwargs):
        self._tcp_server = None
        self._rpc_cons = set()
        self._base_url = base_url
        self._clock = clock
        self._connect_kwargs = connect_kwargs

        # The agents managed by this container.
        # The agents' routers are subrouters of the container's root router.
        self.agents = rpc.ServiceDict()

        # Caches
        self._connections_out_futs = {}  # Futures for outgoing connections
        self._connections_out = {}  # RPC connections to containers by address
        self._remote_agent_futs = {}  # Futures for remote agent validation
        self._remote_agents = {}  # Validated remote agents by connection

    def __str__(self):
        return '%s(%r)' % (self.__class__.__name__, self._base_url)

    @property
    def clock(self):
        """The clock of the container.  Instance of
        :class:`aiomas.clocks.BaseClock`."""
        return self._clock

    def set_server(self, server):
        if self._tcp_server is not None:
            raise RuntimeError('Server already set.')
        self._tcp_server = server

    @asyncio.coroutine
    def connect(self, url, timeout=0):
        """Connect to the argent available at *url* and return a proxy to it.

        *url* is a string ``<protocol>://<addr>//<agent-id>`` (e.g.,
        ``'tcp://localhost:5555/0'``).

        With a *timeout* of 0 (the default), there will only be one connection
        attempt before an error is raised (:exc:`ConnectionRefusedError` for
        TCP sockets and LocalQueue, :exc:`FileNotFoundError` for Unix domain
        sockets).  If you set *timeout* to a number > 0 or ``None``, this
        function will try to connect repeatedly for at most that many seconds
        (or indefinitely) before an error is raised.  Use this if the remote
        agent's container may not yet exist.

        This function is a `coroutine
        <https://docs.python.org/3/library/asyncio-task.html#coroutine>`_.

        """
        addr, aid = self._parse_url(url)

        rpc_con = yield from self._open_connection(addr, timeout)
        remote_agent = yield from self._validate_aid(aid, rpc_con, addr, url)

        return remote_agent

    def shutdown(self, as_coro=False):
        """Close the container's server socket and the RPC services for all
        outgoing TCP connections.

        If *async* is left to ``False``, this method calls
        :meth:`asyncio.BaseEventLoop.run_until_complete()` in order to wait
        until all sockets are closed.

        Set *async* to ``True`` if the event loop is already running (e.g.,
        because you are in a coroutine).  The return value then is a `coroutine
        <https://docs.python.org/3/library/asyncio-task.html#coroutine>`_ that
        you need to ``await`` in order to actually shut the container down::

            await container.shutdown(as_coro=True)

        """
        @asyncio.coroutine
        def _shutdown():
            # Close all outgoing connections
            futs = []
            for con in self._connections_out.values():
                futs.append(con.close())
            yield from asyncio.gather(*futs)

            if self._tcp_server:
                # Request closing the server socket and cancel the services
                self._tcp_server.close()
                for con in self._rpc_cons:
                    con.service.cancel()

                # Wait for server and services to actually terminate
                yield from asyncio.gather(self._tcp_server.wait_closed(),
                                          *[c.service for c in self._rpc_cons])

                self._tcp_server = None
                self._rpc_cons = None

        if as_coro:
            return _shutdown()
        else:
            util.run(_shutdown())

    @router.expose
    def validate_aid(self, aid):
        """Return the class name for the agent represented by *aid* if it
        exists or ``None``."""
        agents = self.agents.dict
        if aid in agents:
            return agents[aid].__class__.__name__

    def _add_to_con_cache(self, rpc):
        """Client-connected-callback for the server socket that adds the RPC
        connection *rpc* to the set of connections."""
        self._rpc_cons.add(rpc)

    def _parse_url(self, url):
        """Parse the agent *url* and return a ``((host, port), agent)`` tuple.

        Raise a :exc:`ValueError` if the URL cannot be parsed.

        """
        try:
            proto, addr_aid = url.split('://', 1)
            assert proto in PROTOCOLS, '%s not in %s' % (proto, PROTOCOLS)

            if proto == 'tcp':
                addr, aid = addr_aid.split('/', 1)
                host, port = addr.rsplit(':', 1)
                if host[0] == '[' and host[-1] == ']':
                    # IPv6 addresses may be surrounded by []
                    host = host[1:-1]
                addr = (host, int(port))

            elif proto == 'ipc':
                assert addr_aid[0] == '['
                addr, aid = addr_aid[1:].split(']/', 1)

            elif proto == 'local':
                queue_id, aid = addr_aid.split('/', 1)
                addr = local_queue.get_queue(queue_id)
                aid = aid

            assert aid, 'No agent ID specified.'

        except (AssertionError, IndexError, ValueError) as e:
            raise ValueError('Cannot parse agent URL "%s": %s' % (url, e))

        return addr, aid

    @asyncio.coroutine
    def _open_connection(self, addr, timeout):
        if addr in self._connections_out:
            # Return cached connection
            rpc_con = self._connections_out[addr]
        elif addr in self._connections_out_futs:
            # Wait for ongoing connection attempt
            rpc_con = yield from self._connections_out_futs[addr]
        else:
            # Open new connection
            fut = asyncio.Future()
            self._connections_out_futs[addr] = fut

            rpc_con = yield from rpc.open_connection(addr,
                                                     rpc_service=self,
                                                     timeout=timeout,
                                                     **self._connect_kwargs)

            # Put connection into the cache
            self._rpc_cons.add(rpc_con)
            self._connections_out[addr] = rpc_con

            # Trigger future and remove it from the cache
            fut.set_result(rpc_con)
            self._connections_out_futs.pop(addr)

            # Initialize caches for remote agents
            self._remote_agents[rpc_con] = weakref.WeakValueDictionary()
            self._remote_agent_futs[rpc_con] = {}

        return rpc_con

    @asyncio.coroutine
    def _validate_aid(self, aid, rpc_con, addr, url):
        remote_agents = self._remote_agents[rpc_con]
        remote_agent_futs = self._remote_agent_futs[rpc_con]

        if aid in remote_agents:
            remote_agent = remote_agents[aid]
        elif aid in remote_agent_futs:
            remote_agent = yield from remote_agent_futs[aid]
        else:
            fut = asyncio.Future()
            remote_agent_futs[aid] = fut

            remote_type = yield from rpc_con.remote.validate_aid(aid)
            if remote_type is None:
                raise ConnectionError('Agent "%s" does not exist in '
                                      'Container(%r)' % (aid, addr))
            remote_agent = getattr(rpc_con.remote.agents, aid)
            remote_agent._str = '%sProxy(%r)' % (remote_type, url)

            remote_agents[aid] = remote_agent
            fut.set_result(remote_agent)
            remote_agent_futs.pop(aid)

        return remote_agent

    def _register(self, agent):
        """Register *agent* with the container."""
        aid = str(len(self.agents.dict))
        url = self._base_url + aid
        self.agents.dict[aid] = agent
        self.agents.router.set_sub_router(agent.router, aid)
        return url


class Agent:
    """Base class for all agents."""

    router = rpc.Service()
    """Descriptor that creates an RPC :class:`~aiomas.rpc.Router` for every
    agent instance.

    You can override this in a sub-class if you need to.  (Usually, you don't.)

    """
    def __init__(self, container):
        if not isinstance(container, Container):
            raise TypeError('"container" must be a "Container" instance but '
                            'is %s' % container)
        addr = container._register(self)
        self.__container = container
        self.__addr = addr
        self.__name = '%s(%r)' % (self.__class__.__name__, addr)

    def __str__(self):
        return self.__name

    @property
    def container(self):
        """The :class:`Container` that the agent lives in."""
        return self.__container

    @property
    def addr(self):
        """The agent's address."""
        return self.__addr
