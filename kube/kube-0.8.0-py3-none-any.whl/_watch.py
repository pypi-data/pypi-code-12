"""Helper functions for WATCH."""

import collections
import enum
import io
import json
import select
import socket
import time
import urllib.parse

import http_parser.parser

from kube import _error


class JSONWatcher:
    """Iterator to help with WATCH on Kubernetes resources.

    This iterator will issue a WATCH command to the given path and
    yield JSON objects as they become available.  The standard
    iterator interface is blocking while the extended :meth:`next`
    interface allows non-blocking use.

    Note that you should only want a resource and not any of it's
    items inside it.  Resources always have a ``*List`` kind.

    :param proxy: The proxy this watcher is for.
    :type proxy: kube.APIServerProxy
    :param path: The path of the resource to watch, see
       :meth:`kube.APIServerProxy.urljoin` for details.
    :type path: str
    :param version: The resourceVersion from which to start watching
       the resource.
    :type version: str
    :param fields: A dict of fields which must match their values.
       This is a limited form of the full fieldSelector format, it is
       limited because filtering is done at client side for
       consistecy.
    :type fields: dict

    :raises kube.APIError: When the API server does not respond
       correctly.

    :ivar cluster: The :class:`kube.Cluster` instance.
    """

    def __init__(self, proxy, *path, version=None, fields=None):
        params = {'watch': 'true'}
        if version:
            params['resourceVersion'] = version
        self._fields = fields if fields else {}
        query = '&'.join(k + '=' + v for k, v in params.items())
        url = urllib.parse.urlsplit(proxy.urljoin(*path) + '?' + query)
        self._buffer = collections.deque()
        self._pending_data = b''
        self._sock = self._connect(url)
        self._parser = self._make_request(self._sock, url)
        self._fill_buffer(timeout=0)

    @staticmethod
    def _connect(url):
        """Connect to the URL and perform the initial request.

        This will create a socket and connect it to the server for the
        URL.

        :param url: The URL to connect too.
        :type url: urllib.parse.SplitResult, the result of
           urllib.parse.spliturl().

        :returns: The connected socket.
        :raises APIError: When failing to connect to the server.
        """
        addrinfo = socket.getaddrinfo(url.hostname, url.port or 80,
                                      type=socket.SOCK_STREAM)
        for family, kind, proto, _, sockaddr in addrinfo:
            sock = socket.socket(family, kind, proto)
            try:
                sock.connect(sockaddr)
            except ConnectionRefusedError:
                sock.close()
                continue
            else:
                return sock
        else:                   # pylint: disable=useless-else-on-loop
            raise _error.APIError('Failed to connect to {}'
                                  .format(urllib.parse.urlunsplit(url)))

    @staticmethod
    def _make_request(sock, url):
        """Make the GET/watch request.

        This performs the initial GET request to start the watch
        operation and reads the headers from the response.  Some of
        the body may already have been read as well and will be
        available in the returned http parser instance.

        :param sock: The connected socket.
        :type sock: socket.socket
        :param url: The split URL from urllib.parse.urlsplit().
        :type url: urllib.parse.SplitResult

        :returns: The HTTP parser instance.
        :rtype: http_parser.parser.HttpParser

        :raises APIError: For errors from the k8s API server.
        """
        request = ('GET {0.path}?{0.query} HTTP/1.1\r\n'
                   'Host: {0.hostname}\r\n'
                   '\r\n'.format(url))
        class DummyReq:
            """Request for APIError purposes."""
            body = request
            status_code = 0
        parser = http_parser.parser.HttpParser()  # pylint: disable=no-member
        sock.send(request.encode('ASCII'))
        while not parser.is_headers_complete():
            data = sock.recv(io.DEFAULT_BUFFER_SIZE)
            if not data:
                raise _error.APIError(DummyReq(), 'Did not receive response')
            nreceived = len(data)
            nparsed = parser.execute(data, nreceived)
            DummyReq.status_code = parser.get_status_code()
            if nparsed != nreceived:
                raise _error.APIError(DummyReq(), 'HTTP parsing failed')
        if not parser.is_chunked():
            raise _error.APIError(DummyReq(), 'Not a chunked HTTP response')
        return parser

    def __iter__(self):
        return self

    def __next__(self):
        """Return the next :class:`kube.WatchEvent` instance.

        This is the equivalent of :meth:`next` with `timeout=None` so
        will block if no more events are queued.
        """
        return self.next()

    def next(self, *, timeout=None):
        """Return the next line.

        :param timeout: If specified a timeout in seconds.  If no new
           event occurred in this time a :class:`TimeoutError` is
           raised.  Set to ``0`` for a non-blocking call.
        :type timeout: int or float.

        :raises TimeoutError: In case retrieving the next event
           timed out.
        """
        if self._buffer:
            return self._buffer.popleft()
        end = time.monotonic() + timeout
        remaining = timeout
        while remaining >= 0:
            self._fill_buffer(timeout=remaining)
            if self._buffer:
                return self._buffer.popleft()
            elif self._sock.fileno() == -1:
                raise StopIteration
            remaining = end - time.monotonic()
        raise TimeoutError

    def skip(self, version):
        """Skip ahead past the given version on the resource.

        This iterates over already buffered events and compares the
        version number of each resource item with the given version.
        If an item with the given version is found, all items up to
        and including the item are dropped from the buffer, otherwise
        the buffer remains unmodified.

        :param version: The resourceVersion of the item you want to
           skip past.
        :type version: bytes

        :raises TypeError: If the objects do not have a valid
           resourceVersion.
        """
        new_buffer = []
        keep = False
        for obj in self._buffer:
            if keep:
                new_buffer.append(obj)
                continue
            try:
                item_version = obj['object']['metadata']['resourceVersion']
            except (KeyError, TypeError) as err:
                raise TypeError('No resourceVersion in object') from err
            else:
                if item_version == version:
                    keep = True
        if new_buffer:
            self._buffer = collections.deque(new_buffer)

    def _fill_buffer(self, *, timeout=None):
        """Fill the buffer with fully received lines.

        This fills :attr:`_buffer` with fully received lines,
        i.e. lines ending in ``\n``.  New data is read regardless of
        whether the buffer already contains lines.  Any partially
        received lines are cached in :attr:`_pending_data` for the
        next call to this method.
        """
        # bytes.split() will return an empty bytestring if the line is
        # already terminated so the last item is always pending data.
        data = self._read_data(timeout=timeout)
        data = self._pending_data + data
        lines = data.split(b'\n')
        self._pending_data = lines.pop(-1)
        for line in lines:
            obj = json.loads(line.decode('utf-8'))
            if not self._match_fields(obj['object']):
                continue
            self._buffer.append(obj)

    def _match_fields(self, obj):
        """Check whether the object matches the fields configured."""
        results = []
        for name, value in self._fields.items():
            item = obj
            for key in name.split('.'):
                try:
                    item = item[key]
                except KeyError:
                    return False
            results.append(item == value)
        return all(results)

    def _read_data(self, *, timeout=None):
        """Read a chunk of data.

        This will try to read all data available.  If no data is
        available it will wait up to *timeout* seconds for data.  Once
        any data is received all available data is returned without
        further delays.

        :param int timeout: The maxium time to wait for data, or wait
           forever if None.

        :returns: The received data or an empty string if no data was
           received.
        :rtype: bytes
        :raises: StopIteration if the socket was closed.
        """
        if self._sock.fileno() == -1:
            return ''
        sock = self._sock
        readers = [sock]
        writers = []
        while True:
            rlist, _, _ = select.select(readers, writers, writers, timeout)
            if not rlist:
                break
            timeout = 0
            chunk = sock.recv(io.DEFAULT_BUFFER_SIZE)
            if not chunk:
                sock.close()
                break
            nreceived = len(chunk)
            nparsed = self._parser.execute(chunk, nreceived)
            if nparsed != nreceived:
                raise _error.APIError('Failed to parse HTTP body')
        return self._parser.recv_body()

    def close(self):
        """Close the iterator.

        This releases the socket.  Once the already buffered data is
        consumed :class:`StopIteration` will be raised.
        """
        self._sock.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_val, exc_type, traceback):
        self.close()


class WatchEventType(enum.Enum):
    """Represents the type of watch event."""
    MODIFIED = 'MODIFIED'
    ADDED = 'ADDED'
    DELETED = 'DELETED'
    ERROR = 'ERROR'


WatchEvent = collections.namedtuple('WatchEvent', ('evtype', 'item'))
WatchEvent.MODIFIED = WatchEventType.MODIFIED
WatchEvent.ADDED = WatchEventType.ADDED
WatchEvent.DELETED = WatchEventType.DELETED
WatchEvent.ERROR = WatchEventType.ERROR
WatchEvent.__doc__ = """\
Represents an event and it's object generated from watching a resource.

:cvar WatchEvent: A convenience alias of :class:`WatchEvent`.

:ivar evtype: The event type enumeration.
:type evtype: :class:`WatchEventType`
:ivar item: The object which is the subject of the event.
:type item: This depends on who created this :class:`WatchEvent`.
"""


class ResourceWatcher:
    """Watcher for a resource.

    This is an iterator yielding watch events in either a blocking or
    non-blocking way, for non-blocking use ``.next(timeout=0)``.  It
    uses a :class:`JSONWatcher` instance for retrieving the actual
    events, which must be configured correctly to return events for
    the same resource as this watcher is for.

    :param cluster: The cluster instance.
    :type cluster: kube.Cluster

    :param jsonwatcher: A correctly configured watcher instance which
       yields the decoded JSON objects.
    :type jsonwatcher: JSONWatcher

    :param itemcls: A constructor for the resource item being watched.
    :type itemcls: A callable, usually a class.
    """

    def __init__(self, cluster, jsonwatcher, itemcls):
        self.cluster = cluster
        self._watcher = jsonwatcher
        self._itemcls = itemcls

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self, *, timeout=None):
        """Return the next watch event.

        :param timeout: The maximum time to wait for a new event.  Not
           specifying this will block forever until a new event
           arrives, otherwise a :class:`TimeoutError` is raised if no
           new event was received in time.
        :type timeout: int or float

        :raises TimeoutError: When no new event is available after the
           specified timeout.
        """
        obj = self._watcher.next(timeout=timeout)
        return WatchEvent(WatchEventType(obj['type']),
                          self._itemcls(self.cluster, obj['object']))

    def close(self):
        """Close the iterator and release it's resources.

        This releases the underlying socket.
        """
        self._watcher.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_val, exc_type, traceback):
        self.close()
