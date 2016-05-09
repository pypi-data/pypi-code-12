"""
The local queue transport roughly mimics a normal TCP transport, but it sends
and receives messages via two :class:`asyncio.Queue` instances.

Its purpose is to aid the development and debugging of complex networking
algorithms and distributed or multi-agent systems.  In contrast to normal
network transports, messages send via the :class:`LocalQueueTransport` will
always arrive in a deterministic order [#]_.

This transport does *not* work across multiple processes and is *not* thread
safe, so it should only be used within a single thread and process.

The easiest way to use it is to create a :class:`LocalQueue` instance via the
:func:`get_queue()` function and pass it to
:func:`aiomas.channel.start_server()`/:func:`aiomas.channel.open_connection()`
or :meth:`aiomas.agent.Container.create()` as *addr* argument.

.. [#] Actually, message sent via a single TCP connection also arrive at a
       deterministic order (this is a property of the TCP/IP protocol).  So
       the LocalQueue transport won't give you any benefits in this case.

       However, if you have multiple connections to the same server and send
       message through them in parallel, it's no longer deterministic in which
       order the messages arrive from the different connections.  In this case,
       the LocalQueue transport can help you.

"""
import asyncio

__all__ = ['get_queue', 'clear_queue_cache',
           'create_connection', 'create_server',
           'LocalQueue', 'LocalQueueServer', 'LocalQueueTransport']


CLOSE_QUEUE = object()
_queues = {}


def get_queue(queue_id):
    """Return a :class:`~aiomas.local_queue.LocalQueue` instance for the given
    *queue_id*.

    If no instance is cached yet, create a new one.

    Queue IDs must be strings and must not contain the ``/`` character.  Raise
    a :exc:`ValueError` if these rules are violated.

    """
    if not isinstance(queue_id, str):
        raise ValueError('Queue ID must be "str" not "%s"' % type(queue_id))

    if '/' in queue_id:
        raise ValueError('"/" not allowed in queue ID (%r)' % queue_id)

    return _queues.setdefault(queue_id, LocalQueue(queue_id))


def clear_queue_cache():
    """Clear the global queue cache."""
    _queues.clear()


@asyncio.coroutine
def create_connection(protocol_factory, lq, *, loop=None, **kwds):
    """Connect to a :class:`LocalQueue` *lq*.

    The *protocol_factory* must be a callable returning a `protocol
    <https://docs.python.org/3/library/asyncio-protocol.html>`_ instance.

    Before a connection to *lq* can be made, a server must
    be started for this instance (see :func:`create_server()`).

    This function is a `coroutine
    <https://docs.python.org/3/library/asyncio-task.html#coroutine>`_ which
    will try to establish the connection in the background.  When successful,
    the coroutine returns a (transport, protocol) pair.

    """
    if loop is None:
        loop = asyncio.get_event_loop()

    client_server_q = asyncio.Queue(loop=loop)
    server_client_q = asyncio.Queue(loop=loop)

    lq.new_connection(sendq=server_client_q, recvq=client_server_q)

    p = protocol_factory()
    t = LocalQueueTransport(lq, sendq=client_server_q, recvq=server_client_q,
                            protocol=p)
    p.connection_made(t)
    return (t, p)


@asyncio.coroutine
def create_server(protocol_factory, lq, **kwds):
    """Create a :class:`LocalQueue` server bound to *lq*.

    The *protocol_factory* must be a callable returning a `protocol
    <https://docs.python.org/3/library/asyncio-protocol.html>`_ instance.

    Return a :class:`LocalQueueServer` instance.  That instance is also set
    as :attr:`~LocalQueue.server` for *lq*.

    This function is a `coroutine
    <https://docs.python.org/3/library/asyncio-task.html#coroutine>`_.

    """
    return LocalQueueServer(protocol_factory, lq)


class LocalQueue:
    """An instance of this class serves as transport description when creating
    a server or connection.

    The functions :func:`create_server()` and :func:`create_connection()` both
    require an instance of this class.  Alternatively, instances of this class
    can be passed as *addr* argument to :func:`aiomas.channel.start_server()`
    and :func:`aiomas.channel.open_connection()`

    A server needs to be started before any connections can be made.

    """
    def __init__(self, queue_id):
        self._queue_id = queue_id
        self._server = None

    def __repr__(self):
        return '<%s.%s object %r at 0x%x>' % (self.__class__.__module__,
                                              self.__class__.__name__,
                                              self._queue_id,
                                              id(self))

    def __str__(self):
        return '%s(%r)' % (self.__class__.__name__, self._queue_id)

    @property
    def queue_id(self):
        """The queue's ID."""
        return self._queue_id

    @property
    def server(self):
        """The :class:`LocalQueueServer` instance that was bound to this
        instance or ``None`` if no server has yet been started.

        """
        return self._server

    def set_server(self, server):
        """Set a :class:`LocalQueueServer` instance.

        Raise a :exc:`RuntimeError` if a server has already been bound to
        this instance.

        This method is called by :func:`create_server()`.

        """
        if self._server is not None:
            raise RuntimeError('Server is already set.')

        self._server = server

    def unset_server(self):
        """Unset the server from this instance.

        This method is called when the server is closed (see
        :class:`LocalQueueServer.close()`).

        """
        self._server = None

    def new_connection(self, sendq, recvq):
        """Create a connection endpoint on the server side.

        This method is called by :func:`create_connection()`.

        *sendq* and *recvq* are the queues used for sending and receiving
        messages to and from the client.

        """
        if self._server is None:
            raise ConnectionRefusedError('No server started for this local '
                                         'queue instance.')
        self._server.new_connection(sendq, recvq)


class LocalQueueServer(asyncio.AbstractServer):
    """Implements ``asyncio.events.AbstractServer``.  An instance of this class
    is returned by :func:`create_server()`.

    *lq* is the :class:`LocalQueue` instance that this server was bound to.

    *protocol_factory* is a callable that is called for each new client
    connection in order to create a new protocol instance.

    """
    def __init__(self, protocol_factory, lq):
        self._protocol_factory = protocol_factory
        self._lq = lq
        lq.set_server(self)

    @property
    def lq(self):
        """The :class:`LocalQueue` the server is bound to."""
        return self._lq

    def new_connection(self, sendq, recvq):
        """Create a new protocol and transport instance.

        Call the *protocol factory*, create a new :class:`LocalQueueTransport`
        with *sendq* and *recvq* and wire them together.

        Called by :func:`create_connection()` via
        :meth:`LocalQueue.new_connection()`.

        """
        p = self._protocol_factory()
        t = LocalQueueTransport(self._lq, sendq, recvq, p)
        p.connection_made(t)

    def close(self):
        """Close the server and unset this instance from the associated
        :class:`LocalQueue` instance.

        """
        self._lq.unset_server()

    @asyncio.coroutine
    def wait_closed(self):
        """Immediately return (there's nothing to wait for).

        This method is a `coroutine
        <https://docs.python.org/3/library/asyncio-task.html#coroutine>`_.

        """
        return


class LocalQueueTransport(asyncio.Transport):
    """Implements ``asyncio.transports.Transport``.

    A *LocalQueueTransport* has to asynchronous queues (instances of
    :class:`asyncio.Queue`) – one for sending messages to the other side
    and one for receiving messages from it.

    """
    def __init__(self, lq, sendq, recvq, protocol):
        super().__init__(extra={'peername': str(lq)})
        self._sendq = sendq
        self._recvq = recvq
        self._protocol = protocol
        self._wait_read = None
        self._task_recv = asyncio.async(self._recv())

    @asyncio.coroutine
    def _recv(self):
        try:
            while self._recvq is not None:
                if self._wait_read is not None:
                    yield from self._wait_read
                data = yield from self._recvq.get()
                if data is CLOSE_QUEUE:
                    self.close()
                    break
                self._protocol.data_received(data)
        except asyncio.CancelledError:
            return

    def close(self):
        """Close the transport.

        Buffered data will be flushed asynchronously.  No more data will be
        received.  After all buffered data is flushed, the protocol's
        ``connection_lost()`` method will (eventually) be called with ``None``
        as its argument.

        """
        if self._sendq is not None:
            sendq = self._sendq
            self._task_recv.cancel()
            self._sendq = None
            self._recvq = None
            sendq.put_nowait(CLOSE_QUEUE)
            self._protocol.connection_lost(None)

    def write(self, data):
        """Write some data bytes to the transport.

        This does not block; it buffers the data and arranges for it to be sent
        out asynchronously.

        """
        self._sendq.put_nowait(data)

    def can_write_eof(self):
        """Return ``False``.  This transport does not support ``write_eof()``.
        """
        return False

    def abort(self):
        """Close the transport immediately.

        Buffered data will be lost.  No more data will be received.  The
        protocol's ``connection_lost()`` method will (eventually) be called
        with ``None`` as its argument.

        """
        self.close()
