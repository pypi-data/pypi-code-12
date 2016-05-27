import logging
import socket
import asyncio

from collections import deque

logger = logging.getLogger(__name__)

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 11300
DEFAULT_PRIORITY = 2 ** 31
DEFAULT_TTR = 120
MAX_CHUNK_SIZE = 65536


class BeanstalkcException(Exception): pass


class UnexpectedResponse(BeanstalkcException):

    def __init__(self, command, status, results):
        super().__init__()
        self.command = command
        self.status = status
        self.results = results


class CommandFailed(BeanstalkcException):

    def __init__(self, command, status, results):
        super().__init__()
        self.command = command
        self.status = status
        self.results = results


class DeadlineSoon(BeanstalkcException): pass
class SocketError(BeanstalkcException): pass


async def create_connection(address, *, loop=None):
    """Creates beanstalk connection.
    Opens connection to Redis server specified by address argument.
    Address argument is similar to socket address argument, ie:
    * when address is a tuple it represents (host, port) pair;
    * when address is a str it represents unix domain socket path.
    (no other address formats supported)
    Encoding argument can be used to decode byte-replies to strings.
    By default no decoding is done.
    Return value is BeanstalkConnection instance.
    This function is a coroutine.
    """
    assert isinstance(address, (tuple, list, str)), "tuple or str expected"

    if isinstance(address, (list, tuple)):
        host, port = address
        logger.debug("Creating tcp connection to %r", address)
        reader, writer = await asyncio.open_connection(
            host, port, loop=loop)
        sock = writer.transport.get_extra_info('socket')
        if sock is not None:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    else:
        raise ValueError("Unix socket support not working, sorry")

    conn = BeanstalkConnection(reader, writer, loop=loop)
    return conn


if hasattr(asyncio, 'ensure_future'):
    async_task = asyncio.ensure_future
else:
    async_task = asyncio.async

# NOTE: never put here anything else;
#       just this basic types
_converters = {
    bytes: lambda val: val,
    bytearray: lambda val: val,
    str: lambda val: val.encode('utf-8'),
    int: lambda val: str(val).encode('utf-8'),
    float: lambda val: str(val).encode('utf-8'),
    }


def _set_result(fut, result):
    if fut.done():
        logger.debug("Waiter future is already done %r", fut)
        assert fut.cancelled(), (
            "waiting future is in wrong state", fut, result)
    else:
        fut.set_result(result)


def _set_exception(fut, exception):
    if fut.done():
        logger.debug("Waiter future is already done %r", fut)
        assert fut.cancelled(), (
            "waiting future is in wrong state", fut, exception)
    else:
        fut.set_exception(exception)


def _bytes_len(sized):
    return str(len(sized)).encode('utf-8')


def encode_command(*args):
    """Encodes arguments into redis bulk-strings array.
    Raises TypeError if any of args not of bytes, str, int or float type.
    """
    buf = bytearray()

    def add(data):
        return buf.extend(data + b'\r\n')

    add(b'*' + _bytes_len(args))
    for arg in args:
        if type(arg) in _converters:
            barg = _converters[type(arg)](arg)
            add(b'$' + _bytes_len(barg))
            add(barg)
        else:
            raise TypeError("Argument {!r} expected to be of bytes,"
                            " str, int or float type".format(arg))
    return buf


class Job(object):

    def __init__(self, conn, jid, body):
        self.conn = conn
        self.jid = jid
        self.body = body


def _cast_to_int(f):
    f2 = asyncio.Future()

    def wrapper(f):
        try:
            f2.set_result(int(f.result()))
        except Exception as e:
            f2.set_exception(e)

    f.add_done_callback(wrapper)
    return f2


class BeanstalkConnection(object):
    """Beanstalk connection."""

    def __init__(self, reader, writer, *, loop=None):
        if loop is None:
            loop = asyncio.get_event_loop()
        self._reader = reader
        self._writer = writer
        self._loop = loop
        self._waiters = deque()

        self._parse_yaml = __import__('yaml').load

        self._reader_task = async_task(self._read_data(), loop=self._loop)
        self._db = 0
        self._closing = False
        self._closed = False
        self._close_waiter = asyncio.Future(loop=self._loop)
        self._reader_task.add_done_callback(self._close_waiter.set_result)

    async def _read_body(self, size):
        body = await self._reader.read(size)
        await self._reader.read(2) # trailing crlf
        if size > 0 and not body:
            raise SocketError()
        return body

    async def _interact_value(self, results):
        try:
            return results[0]
        except IndexError:
            # some commands (delete) do not return anything
            return True

    async def _interact_job(self, results):
        jid, size = results
        body = await self._read_body(int(size))
        return Job(self, int(jid), body)

    async def _interact_yaml(self, results):
        size, = results
        body = await self._read_body(int(size))
        return self._parse_yaml(body)

    async def _read_data(self):
        """Response reader task."""
        while not self._reader.at_eof():
            try:
                line = await self._reader.readline()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                # XXX: for QUIT command connection error can be received
                #       before response
                logger.error("Exception on data read %r", exc, exc_info=True)
                break

            try:
                await self._process_line(line)
            except UnexpectedResponse as exc:
                # ProtocolError is fatal
                # so connection must be closed
                self._closing = True
                self._loop.call_soon(self._do_close, exc)
                return

        self._closing = True
        self._loop.call_soon(self._do_close, None)

    async def _process_line(self, line):
        """Processes command results."""

        line = line.decode('UTF-8')
        response = line.split()
        status, results = response[0], response[1:]

        waiter, context = self._waiters.popleft()

        try:
            command = context['command']
            expected_ok = context['expected_ok']
            expected_err = context['expected_err']
            cb = context['cb']

            if status in expected_ok:
                obj = await cb(results)
            elif expected_err and status in expected_err:
                raise CommandFailed(command.split()[0], status, results)
            else:
                raise UnexpectedResponse(command.split()[0], status, results)
        except Exception as exc:
            _set_exception(waiter, exc)
            return

        _set_result(waiter, obj)

    def execute(self, command, expected_ok, expected_err=None, response_type=None):
        """Executes beanstalk command and returns Future waiting for the answer.
        Raises:
        * TypeError if any of args can not be encoded as bytes.
        * ReplyError on redis '-ERR' resonses.
        * ProtocolError when response can not be decoded meaning connection
          is broken.
        """
        if self._reader is None or self._reader.at_eof():
            raise BeanstalkcException("Connection closed or corrupted")
        if command is None:
            raise TypeError("command must not be None")
        if not expected_ok:
            raise TypeError("expected_ok must be have at least one expected response")

        cb = self._interact_value
        if response_type == 'job':
            cb = self._interact_job
        elif response_type == 'yaml':
            cb = self._interact_yaml

        context = {
            'command': command,
            'expected_ok': expected_ok,
            'expected_err': expected_err,
            'cb': cb
        }

        fut = asyncio.Future(loop=self._loop)
        self._writer.write(command.encode('utf-8'))
        self._writer.write(b'\r\n')
        self._waiters.append((fut, context))
        return fut

    def close(self):
        """Close connection."""
        self._do_close(None)

    def _do_close(self, exc):
        if self._closed:
            return
        self._closed = True
        self._closing = False
        self._writer.transport.close()
        self._reader_task.cancel()
        self._reader_task = None
        self._writer = None
        self._reader = None
        while self._waiters:
            waiter, *spam = self._waiters.popleft()
            logger.debug("Cancelling waiter %r", (waiter, spam))
            if exc is None:
                waiter.cancel()
            else:
                waiter.set_exception(exc)

    @property
    def closed(self):
        """True if connection is closed."""
        closed = self._closing or self._closed
        if not closed and self._reader and self._reader.at_eof():
            self._closing = closed = True
            self._loop.call_soon(self._do_close, None)
        return closed

    async def wait_closed(self):
        return await asyncio.shield(self._close_waiter, loop=self._loop)

    async def get_atomic_connection(self):
        return self

    def stats(self):
        """Return a dict of beanstalkd statistics."""
        return self.execute('stats', ['OK'], response_type='yaml')

    def use(self, name):
        """Use a given tube."""
        return self.execute('use {}'.format(name), ['USING'])

    def using(self):
        """Return the tube currently being used."""
        return self.execute('list-tube-used', ['USING'])

    def watch(self, name):
        """Watch a given tube."""
        f = self.execute('watch %s' % name, ['WATCHING'])
        return _cast_to_int(f)

    def watching(self):
        """Return a list of all tubes being watched."""
        return self.execute('list-tubes-watched', ['OK'], response_type='yaml')

    def put(self, body, priority=DEFAULT_PRIORITY, delay=0, ttr=DEFAULT_TTR):
        """Put a job into the current tube. Returns job id."""
        assert isinstance(body, str), 'Job body must be a str instance'
        jid = self.execute('put %d %d %d %d\r\n%s' % (
                                       priority, delay, ttr, len(body), body),
                                   ['INSERTED'],
                                   expected_err=['JOB_TOO_BIG', 'BURIED', 'DRAINING'],
                           )
        return _cast_to_int(jid)

    def reserve(self, timeout=None):
        """Reserve a job from one of the watched tubes, with optional timeout
        in seconds. Returns a Job object, or None if the request times out."""
        if timeout is not None:
            command = 'reserve-with-timeout %d' % timeout
        else:
            command = 'reserve'

        f = self.execute(command,
                            ['RESERVED'],
                            expected_err=['DEADLINE_SOON', 'TIMED_OUT'],
                            response_type='job'
                            )

        f2 = asyncio.Future()

        def wrapper(f):
            try:
                if not f2.done():
                    f2.set_result(f.result())
            except CommandFailed as e:
                # on a timed-out or deadline soon, just mark it
                if e.status == 'TIMED_OUT':
                    if not f2.done():
                        f2.set_result(None)
                elif e.status == 'DEADLINE_SOON':
                    #f2.set_exception(DeadlineSoon())
                    # deadline soon useless in the context of the current call, maybe fire
                    # it on a listener, for now we'll swallow it
                    if not f2.done():
                        f2.set_result(None)
            except Exception as e:
                if not f2.done():
                    f2.set_exception(e)

        f.add_done_callback(wrapper)
        return f2

    def delete(self, jid):
        """Delete a job, by job id."""
        return self.execute('delete {}'.format(jid), ['DELETED'], ['NOT_FOUND'])

    def bury(self, jid, priority=DEFAULT_PRIORITY):
        """Bury a job, by job id."""
        return self.execute('bury %d %d' % (jid, priority), ['BURIED'], ['NOT_FOUND'])

    def ignore(self, name):
        """Stop watching a given tube."""
        f = self.execute('ignore %s' % name, ['WATCHING'], ['NOT_IGNORED'])

        f2 = asyncio.Future()

        def wrapper(f):
            try:
                f2.set_result(int(f.result()))
            except CommandFailed:
                f2.set_result(1)
            except Exception as e:
                f2.set_exception(e)

        f.add_done_callback(wrapper)
        return f2

