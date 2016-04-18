"""
This module implements and asyncio :class:`asyncio.Protocol` protocol for a
request-reply :class:`Channel`.

"""
from asyncio import coroutine
import asyncio
import collections
import itertools
import logging
import struct
import time
import traceback

from . import codecs
from . import local_queue
from .exceptions import RemoteException

__all__ = [
    'REQUEST', 'RESULT', 'EXCEPTION', 'DEFAULT_CODEC',
    'open_connection', 'start_server',
    'Header', 'Request', 'Channel', 'ChannelProtocol',
]


# Message types
REQUEST = 0
RESULT = 1
EXCEPTION = 2

DEFAULT_CODEC = codecs.JSON

Header = struct.Struct('!L')

logger = logging.getLogger(__name__)


@coroutine
def open_connection(addr, *,
                    loop=None, codec=None, extra_serializers=(), timeout=0,
                    **kwds):
    """Return a :class:`Channel` connected to *addr*.

    This is a convenience wrapper for
    :meth:`asyncio.BaseEventLoop.create_connection()`,
    :meth:`asyncio.BaseEventLoop.create_unix_connection()`, and
    :func:`aiomas.local_queue.create_connection()`.

    If *addr* is a tuple ``(host, port)``, a TCP connection will be created.
    If *addr* is a string, it should be a path name pointing to the unix domain
    socket to connect to.
    If *addr* is a :mod:`aiomas.local_queue` instance, a *LocalQueue*
    connection will be created.

    You can optionally provide the event *loop* to use.

    By default, the :class:`~aiomas.codecs.JSON` *codec* is used.  You
    can override this by passing any subclass of :class:`aiomas.codecs.Codec`
    as *codec*.

    You can also pass a list of *extra_serializers* for the codec.  The list
    entires need to be callables that return a tuple with the arguments for
    :meth:`~aiomas.codecs.Codec.add_serializer()`.

    With a *timeout* of 0 (the default), there will only be one connection
    attempt before an error is raised (:exc:`ConnectionRefusedError` for TCP
    sockets and LocalQueue, :exc:`FileNotFoundError` for Unix domain sockets).
    If you set *timeout* to a number > 0 or ``None``, this function will try to
    connect repeatedly for at most that many seconds (or indefinitely) before
    an error is raised.  Use this if you need to start the client before the
    server.

    The remaining keyword argumens *kwds* are forwarded to
    :meth:`asyncio.BaseEventLoop.create_connection()` and
    :meth:`asyncio.BaseEventLoop.create_unix_connection` respectively.

    This function is a `coroutine
    <https://docs.python.org/3/library/asyncio-task.html#coroutine>`_.

    """
    if loop is None:
        loop = asyncio.get_event_loop()

    if timeout is None:
        timeout = float('inf')

    codec = codec() if codec else DEFAULT_CODEC()
    for s in extra_serializers:
        codec.add_serializer(*s())

    def factory():
        return ChannelProtocol(codec, loop=loop)

    # Get the appropriate connect function and its arguments:
    if type(addr) is tuple:
        connect = loop.create_connection
        args = (factory,) + addr
        kwargs = kwds
        # If you connect to "localhost", some systems try to connect to
        # 127.0.0.1 and ::1 resulting in an OSError(Multiple errors occured),
        # that wraps two ConnectionRefusedErrors:
        ConnectionRefused = (ConnectionRefusedError, OSError)
    elif type(addr) is str:
        connect = loop.create_unix_connection
        args = (factory, addr)
        kwargs = kwds
        ConnectionRefused = FileNotFoundError
    elif isinstance(addr, local_queue.LocalQueue):
        connect = local_queue.create_connection
        args = (factory, addr)
        kwargs = dict(kwds, loop=loop)
        ConnectionRefused = ConnectionRefusedError
    else:
        raise ValueError('Unknown address type: %s' % addr)

    t, p = yield from _try_connect(connect, args, kwargs, ConnectionRefused,
                                   timeout)

    return p.channel


@coroutine
def start_server(addr, client_connected_cb, *,
                 loop=None, codec=None, extra_serializers=(), **kwds):
    """Start a server listening on *addr* and call *client_connected_cb*
    for every client connecting to it.

    This function is a convenience wrapper for
    :meth:`asyncio.BaseEventLoop.create_server()`,
    :meth:`asyncio.BaseEventLoop.create_unix_server()`, and
    :func:`aiomas.local_queue.create_server()`.

    If *addr* is a tuple ``(host, port)``, a TCP socket will be created.
    If *addr* is a string, a unix domain socket at this path will be created.
    If *addr* is a :mod:`aiomas.local_queue` instance, a *LocalQueue* server
    will be created.

    The single argument of the callable *client_connected_cb* is a new instance
    of :class:`Channel`.

    You can optionally provide the event *loop* to use.

    By default, the :class:`~aiomas.codecs.JSON` *codec* is used.  You can
    override this by passing any subclass of :class:`aiomas.codecs.Codec` as
    *codec*.

    You can also pass a list of *extra_serializers* for the codec.  The list
    entires need to be callables that return a tuple with the arguments for
    :meth:`~aiomas.codecs.Codec.add_serializer()`.

    The remaining keyword argumens *kwds* are forwarded to
    :meth:`asyncio.BaseEventLoop.create_server()` and
    :meth:`asyncio.BaseEventLoop.create_unix_server` respectively.

    This function is a `coroutine
    <https://docs.python.org/3/library/asyncio-task.html#coroutine>`_.

    """
    if loop is None:
        loop = asyncio.get_event_loop()

    if not codec:
        codec = DEFAULT_CODEC

    def factory():
        c = codec()
        for s in extra_serializers:
            c.add_serializer(*s())
        return ChannelProtocol(c, client_connected_cb, loop=loop)

    if type(addr) is tuple:
        return (yield from loop.create_server(factory, *addr, **kwds))
    elif type(addr) is str:
        return (yield from loop.create_unix_server(factory, addr, **kwds))
    elif isinstance(addr, local_queue.LocalQueue):
        return (yield from local_queue.create_server(factory, addr, **kwds))
    else:
        raise ValueError('Unknown address type: %s' % addr)


@asyncio.coroutine
def _try_connect(open_connection, args, kwargs, ConnectionRefused, timeout):
    """Try to establish a connection and return the *(transport, protocol)*
    pair if successful.

    Repeatedly call *open_connection(\*args, \*\*kwargs)*.  If not connection
    can be opened for *timeout* seconds, re-raise the connection error from
    *open_connection* (which is of type *ConnectionRefused*).

    """
    retry_interval = 0.5
    start_time = time.monotonic()
    while True:
        try:
            t, p = yield from open_connection(*args, **kwargs)
            break
        except ConnectionRefused:
            if (time.monotonic() - start_time) > timeout:
                raise

            logger.debug('Could not connect.  Retrying in %.2fs ...',
                         retry_interval)
            yield from asyncio.sleep(retry_interval)
            retry_interval = min(30, 1.5 * retry_interval)  # Wait at most 30s

    return t, p


def _get_checked_msg_len(msg):
    """Return the number of bytes/length of *msg*.

    Raise a exc:`ValueError` if the length is to large for :class:`Header`.

    """
    msg_len = len(msg)
    try:
        len_bytes = Header.pack(msg_len)
    except struct.error:
        max_size = 2 ** (Header.size * 8)
        raise ValueError('Serialized message is too long (%d).  Maximum '
                         'length is %d.' % (msg_len, max_size)) from None

    return len_bytes


class ChannelProtocol(asyncio.Protocol):
    """Asyncio :class:`asyncio.Protocol` which connects the low level transport
    with the high level :class:`Channel` API.

    The *codec* is used to (de)serialize messages.  It should be a sub-class of
    :class:`aiomas.codecs.Codec`.

    Optionally you can also pass a function/coroutine *client_connected_cb*
    that will be executed when a new connection is made (see
    :func:`start_server()`).

    """
    def __init__(self, codec, client_connected_cb=None, *, loop):
        super().__init__()
        self.codec = codec
        self.transport = None
        self.channel = None
        self._client_connected_cb = client_connected_cb
        self._loop = loop
        self._buffer = bytearray()
        self._read_size = None

        # For flow control
        self._paused = False
        self._drain_waiter = None
        self._connection_lost = None
        self._out_msgs = asyncio.Queue()
        self._task_process_out_msgs = None

    def connection_made(self, transport):
        """Create a new :class:`Channel` instance for a new connection.

        Also call the *client_connected_cb* if one was passed to this class.

        """
        self._task_process_out_msgs = asyncio.async(self._process_out_msgs())

        self.transport = transport
        self.channel = Channel(self, self.codec, transport, loop=self._loop)

        if self._client_connected_cb is not None:
            res = self._client_connected_cb(self.channel)
            if asyncio.iscoroutine(res):
                asyncio.async(res, loop=self._loop)

    def connection_lost(self, exc):
        """Set a :exc:`ConnectionError` to the :class:`Channel` to indicate
        that the connection is closed."""
        if exc is None:  # pragma: no branch
            exc = ConnectionResetError('Connection closed')
        self.channel._set_exception(exc)
        self._connection_lost = exc
        self._task_process_out_msgs.cancel()

        # Wake up the writer if currently paused.
        if not self._paused:
            return
        waiter = self._drain_waiter
        if waiter is None:
            return
        self._drain_waiter = None
        if waiter.done():
            return
        waiter.set_exception(exc)

    def data_received(self, data):
        """Buffer incomming data until we have a complete message and then
        pass it to :class:`Channel`.

        Messages are fixed length.  The first four bytes (in network byte
        order) encode the length of the following payload.  The payload is
        a triple ``(msg_type, msg_id, content)`` encoded with the specified
        *codec*.

        """
        self._buffer.extend(data)
        while True:
            # We may have more then one message in the buffer,
            # so we loop over the buffer until we got all complete messages.

            if self._read_size is None and len(self._buffer) >= Header.size:
                # Received the complete header of a new message
                self._read_size = Header.unpack_from(self._buffer)[0]
                # TODO: Check for too large messages?
                self._read_size += Header.size

            if self._read_size and len(self._buffer) >= self._read_size:
                # At least one complete message is in the buffer
                data = self._buffer[Header.size:self._read_size]
                self._buffer = self._buffer[self._read_size:]
                self._read_size = None
                msg_type, msg_id, content = self.codec.decode(data)
                try:
                    self.channel._feed_data(msg_type, msg_id, content)
                except RuntimeError as exc:
                    self.channel._set_exception(exc)

            else:
                # No complete message in the buffer. We are done.
                break

    def eof_received(self):
        """Set a :exc:`ConnectionResetError` to the :class:`Channel`."""
        # In previous revisions, an IncompleteMessage error was raised if we
        # already received the beginning of a new message. However, having
        # to types of exceptions raised by this methods makes things more
        # complicated for the user. The benefit of the IncompleteMessage was
        # not big enough.
        self.channel._set_exception(ConnectionResetError())

    @coroutine
    def write(self, len_bytes, content):
        """Serialize *content* and write the result to the transport.

        This method is a `coroutine
        <https://docs.python.org/3/library/asyncio-task.html#coroutine>`_.

        """
        assert self._connection_lost is None
        content = len_bytes + content
        done = asyncio.Future()
        self._out_msgs.put_nowait((done, content))
        yield from done

    def pause_writing(self):
        """Set the *paused* flag to ``True``.

        Can only be called if we are not already paused.

        """
        assert not self._paused
        self._paused = True
        if self._loop.get_debug():
            logger.debug("%r pauses writing", self)

    def resume_writing(self):
        """Set the *paused* flat to ``False`` and trigger the waiter future.

        Can only be called if we are paused.

        """
        assert self._paused
        self._paused = False
        if self._loop.get_debug():
            logger.debug("%r resumes writing", self)

        waiter = self._drain_waiter
        if waiter is not None:
            self._drain_waiter = None
            if not waiter.done():
                waiter.set_result(None)

    @coroutine
    def _process_out_msgs(self):
        try:
            while True:
                done, content = yield from self._out_msgs.get()
                self.transport.write(content)
                yield from self._drain_helper()
                done.set_result(None)
        except asyncio.CancelledError:
            assert self._connection_lost is not None

    @coroutine
    def _drain_helper(self, before=False):
        if self._connection_lost is not None:
            raise self._connection_lost
        if not self._paused:
            return
        waiter = self._drain_waiter
        assert waiter is None or waiter.cancelled()
        waiter = asyncio.Future(loop=self._loop)
        self._drain_waiter = waiter
        yield from waiter


class Request:
    """Represents a request returned by :meth:`Channel.recv()`.  You shoudn't
    instantiate it yourself.

    *content* contains the incoming message.

    *msg_id* is the ID for that message.  It is unique within a channel.

    *protocol* is the channel's :class:`ChannelProtocol` instance that is used
    for writing back the reply.

    To reply to that request you can ``yield from`` :meth:`Request.reply()`
    or :meth:`Request.fail()`.

    """
    def __init__(self, content, message_id, protocol):
        self._content = content
        self._msg_id = message_id
        self._protocol = protocol

    @property
    def content(self):
        """The content of the incoming message."""
        return self._content

    @coroutine
    def reply(self, result):
        """Reply to the request with the provided result.

        This method is a `coroutine
        <https://docs.python.org/3/library/asyncio-task.html#coroutine>`_.

        """
        protocol = self._protocol
        if protocol._connection_lost is not None:
            raise protocol._connection_lost

        content = (RESULT, self._msg_id, result)
        try:
            content = protocol.codec.encode(content)
            msg_len = _get_checked_msg_len(content)

        except Exception as e:
            return (yield from self.fail(e))
        else:
            yield from protocol.write(msg_len, content)

    @coroutine
    def fail(self, exception):
        """Indicate a failure described by the *exception* instance.

        This will raise a :exc:`~aiomas.exceptions.RemoteException` on the
        other side of the channel.

        This method is a `coroutine
        <https://docs.python.org/3/library/asyncio-task.html#coroutine>`_.

        """
        protocol = self._protocol
        if protocol._connection_lost is not None:
            raise protocol._connection_lost

        stacktrace = traceback.format_exception(exception.__class__, exception,
                                                exception.__traceback__)
        content = (EXCEPTION, self._msg_id, ''.join(stacktrace))
        content = protocol.codec.encode(content)
        msg_len = _get_checked_msg_len(content)
        yield from protocol.write(msg_len, content)


class Channel:
    """A Channel represents a request-reply channel between two endpoints. An
    instance of it is returned by :func:`open_connection()` or is passed to the
    callback of :func:`start_server()`.

    *protocol* is an instance of :class:`ChannelProtocol`.

    *transport* is an :class:`asyncio.BaseTransport`.

    *loop* is an instance of an :class:`asyncio.BaseEventLoop`.

    """
    def __init__(self, protocol, codec, transport, loop):
        self._protocol = protocol
        self._codec = codec
        self._transport = transport
        self._loop = loop

        self._message_id = itertools.count()
        self._out_messages = {}  # message_id -> message
        self._in_queue = collections.deque()
        self._waiter = None  # A future.
        self._exception = None

    @property
    def codec(self):
        """The codec used to de-/encode messages send via the channel."""
        return self._codec

    @property
    def transport(self):
        """The transport of this channel (see the `Python documentation
        <https://docs.python.org/3/library/asyncio-protocol.html#transports>`_
        for details).

        """
        return self._transport

    def send(self, content):
        """Send a request *content* to the other end and return a future which
        is triggered when a reply arrives.

        One of the following exceptions may be raised:

        - :exc:`ValueError` if the message is too long (the length of the
          encoded message does not fit into a *long*, which is ~ 4 GiB).

        - :exc:`~aiomas.exceptions.RemoteException`: The remote site raised an
          exception during the computation of the result.

        - :exc:`ConnectionError` (or its subclass :exc:`ConnectionResetError`):
          The connection was closed during the request.

        - :exc:`RuntimeError`:

          - If an invalid message type was received.

          - If the future returned by this method was already triggered or
            canceled by a third party when an answer to the request arrives
            (e.g., if a task containing the future is cancelled).  You get
            more detailed exception messages if you `enable asyncio's debug
            mode`__

            __ https://docs.python.org/3/library/asyncio-dev.html

        .. code-block:: python

           try:
               result = yield from channel.request('ohai')
           except RemoteException as exc:
               print(exc)

        """
        if self._exception is not None:
            raise self._exception

        message_id = next(self._message_id)
        out_message = asyncio.Future(loop=self._loop)
        if self._loop.get_debug():
            self._out_messages[message_id] = (out_message, content)
        else:
            self._out_messages[message_id] = out_message

        data = self._codec.encode((REQUEST, message_id, content))
        try:
            msg_len = _get_checked_msg_len(data)
        except ValueError:
            del self._out_messages[message_id]
            out_message.cancel()
            raise

        asyncio.async(self._protocol.write(msg_len, data), loop=self._loop)

        return out_message

    @coroutine
    def recv(self):
        """Wait for an incoming :class:`Request` and return it.

        May raise one of the following exceptions:


        - :exc:`ConnectionError` (or its subclass :exc:`ConnectionResetError`):
          The connection was closed during the request.

        - :exc:`RuntimeError`: If two processes try to read from the same
          channel or if an invalid message type was received.

        This method is a `coroutine
        <https://docs.python.org/3/library/asyncio-task.html#coroutine>`_.

        """
        if self._exception is not None:
            raise self._exception

        if not self._in_queue:
            if self._waiter is not None:
                raise RuntimeError('recv() called while another coroutine is '
                                   'already waiting for incoming data.')
            self._waiter = asyncio.Future(loop=self._loop)
            try:
                yield from self._waiter
            finally:
                # In case of an exception, "self._waiter" is already set to
                # "None" by "self._set_exception()":
                self._waiter = None

        return self._in_queue.popleft()

    def _close(self):
        """Close the channel's transport."""
        if self._transport is not None:
            transport = self._transport
            self._transport = None
            return transport.close()

    @coroutine
    def close(self):
        """`Coroutine
        <https://docs.python.org/3/library/asyncio-task.html#coroutine>`_ that
        closes the channel and waits for all sub tasks to finish."""
        self._close()
        try:
            yield from self._protocol._task_process_out_msgs
            if self._loop.get_debug():
                futs = [m[0] for m in self._out_messages.values()]
            else:
                futs = self._out_messages.values()
            yield from asyncio.gather(*futs, return_exceptions=True)
        except asyncio.CancelledError:
            pass

    def get_extra_info(self, name, default=None):
        """Wrapper for :meth:`asyncio.BaseTransport.get_extra_info()`."""
        return self._transport.get_extra_info(name, default)

    def _feed_data(self, msg_type, msg_id, content):
        """Called by :class:`ChannelProtocol` when a new message arrived."""
        if msg_type == REQUEST:
            # Received new request
            message = Request(content, msg_id, self._protocol)
            self._in_queue.append(message)

            waiter = self._waiter
            if waiter is not None:
                self._waiter = None
                waiter.set_result(False)

        elif msg_type == RESULT or msg_type == EXCEPTION:
            # Received reply to a request
            if self._loop.get_debug():
                message, req = self._out_messages.pop(msg_id)
            else:
                message = self._out_messages.pop(msg_id)
            if message.done():
                errmsg = 'Request reply already set.'
                if message.cancelled():
                    errmsg = 'Request was cancelled.'
                if self._loop.get_debug():
                    errmsg += ' Request: %s; Reply: %s' % (req, content)
                raise RuntimeError(errmsg)

            if msg_type == RESULT:
                message.set_result(content)
            else:
                origin = self.get_extra_info('peername')
                message.set_exception(RemoteException(origin, content))

        else:
            raise RuntimeError('Invalid message type %d' % msg_type)

    def _set_exception(self, exc):
        """Set an exception as result for all futures managed by the Channel
        in order to stop all coroutines from reading/writing to the socket."""
        self._exception = exc

        # Set exception to wait-recv future
        waiter = self._waiter
        if waiter is not None:
            self._waiter = None
            if not waiter.cancelled():
                waiter.set_exception(exc)

        # Set exception to all message futures which wait for a reply
        for msg in self._out_messages.values():
            if self._loop.get_debug():
                msg, _ = msg
            if not msg.done():
                msg.set_exception(exc)

        self._close()
