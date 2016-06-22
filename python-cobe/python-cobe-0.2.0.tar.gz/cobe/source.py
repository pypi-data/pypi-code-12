"""Streaming API source.

This module provides :class:`Source` class to handle communication via
the Streaming API to a receiver in order to send entity updates.
"""

import functools
import logging
import pathlib
import unicodedata
import urllib
import time
import warnings

import msgpack
import voluptuous
import zmq
import zmq.auth

import cobe.model
import cobe.ueid


log = logging.getLogger(__name__)


def _re_raise(*exceptions, become):
    """Decorator to re-raise exceptions as new types.

    This returns a decorator which will catch all of the given exceptions
    raised by the wrapped function and re-raise them as a new exception type.
    The new exception will inherit the message from the caught exception.

    :param exceptions: The exception types to catch from the wrapped
    :param become: The new exeception type to raise.
    """

    def decorator(function):

        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except exceptions as exc:
                raise become(str(exc)) from exc

        return wrapper

    return decorator


def _printable(string):
    """Validate that a string is printable.

    A string is printable if it doesn't contain a ``/`` or characters which
    have the general categories of C or Z.

    :param string: The Unicode string to check for unprintable characters.
    :type string: str

    :returns: The given string as-is.

    :raises voluptuous.Invalid: If the string is not printable.
    """
    for character in string:
        category = unicodedata.category(character)[0]
        if category in ('C', 'Z') or character == '/':
            raise voluptuous.Invalid('Contains unprintable characters')
    return string


_PROTOCOL_VERSION = b'streamapi/4'
_SCHEMA_NIL = voluptuous.Schema(None)
_SCHEMA_BOOL = voluptuous.Schema(bool)
_SCHEMA_NUMBER = voluptuous.Any(int, float)
_SCHEMA_UNICODE = voluptuous.Schema(str)
_SCHEMA_BYTES = voluptuous.Schema(bytes)
_SCHEMA_UEID = voluptuous.All(cobe.ueid.UEID, lambda ueid: str(ueid))
_SCHEMA_PRIMITIVE = voluptuous.Any(
    _SCHEMA_NIL,
    _SCHEMA_BOOL,
    _SCHEMA_NUMBER,
    _SCHEMA_UNICODE,
    _SCHEMA_BYTES,
    _SCHEMA_UEID,
)
_SCHEMA_ARRAY = [_SCHEMA_PRIMITIVE]
_SCHEMA_MAPPING = voluptuous.Any(
    {},
    voluptuous.Schema({
        _SCHEMA_UNICODE: _SCHEMA_PRIMITIVE,
    }, required=True),
)
_SCHEMA_COMPOSITE = voluptuous.Any(_SCHEMA_ARRAY, _SCHEMA_MAPPING)
_SCHEMA_PRINTABLE = voluptuous.All(_SCHEMA_UNICODE, _printable)
_SCHEMA_TRAITS = voluptuous.All(
    set,
    lambda set_: list(set_),
    [_SCHEMA_PRINTABLE],
)
_SCHEMA_IDENTIFIABLE = voluptuous.All(
    voluptuous.Any(cobe.model.Identifier, cobe.model.Update),
    _re_raise(
        cobe.ueid.UEIDError,
        become=voluptuous.Invalid,
    )(lambda entity: entity.ueid()),
    _SCHEMA_UEID,
)
_SCHEMA_ATTRIBUTE = voluptuous.All(
    cobe.model.Attribute,
    voluptuous.Any(
        voluptuous.All(  # Set
            lambda attribute: {
                'value': attribute.value,
                'traits': attribute.traits,
                'deleted': attribute.is_deleted(),
            },
            {
                'value': voluptuous.Any(
                    _SCHEMA_PRIMITIVE,
                    _SCHEMA_COMPOSITE,
                ),
                'traits': _SCHEMA_TRAITS,
                'deleted': voluptuous.Literal(False),
            },
        ),
        voluptuous.All(  # Delete
            lambda attribute: {'deleted': attribute.is_deleted()},
            {'deleted': voluptuous.Literal(True)},
        ),
    ),
)
_SCHEMA_ATTRIBUTES = voluptuous.All(
    cobe.model.Attributes,
    lambda attributes: {name: attributes[name] for name in attributes},
    voluptuous.Schema({
        _SCHEMA_PRINTABLE: _SCHEMA_ATTRIBUTE,
    }, extra=voluptuous.ALLOW_EXTRA),
)
_SCHEMA_RELATIONSHIPS = voluptuous.All(
    tuple,
    lambda set_: list(set_),
    [voluptuous.Any(_SCHEMA_UEID, _SCHEMA_IDENTIFIABLE)],
)
_SCHEMA_UPDATE = voluptuous.Schema({
    voluptuous.Required('ueid'): _SCHEMA_IDENTIFIABLE,
    'timestamp': _SCHEMA_NUMBER,
    voluptuous.Required('exists'): _SCHEMA_BOOL,
    voluptuous.Required('type'): _SCHEMA_PRINTABLE,
    'ttl': _SCHEMA_NUMBER,
    'label': _SCHEMA_UNICODE,
    voluptuous.Required('attrs'): _SCHEMA_ATTRIBUTES,
    voluptuous.Required('parents'): _SCHEMA_RELATIONSHIPS,
    voluptuous.Required('children'): _SCHEMA_RELATIONSHIPS,
})



class SourceError(Exception):
    """Base exception raised for all source errors."""


class TokenError(SourceError):
    """Raised for errors relating to authentication tokens."""


class ProtocolError(SourceError):
    """Raised when an operation would result in a protocol violation."""


class Token:
    """Connection authentication token.

    These tokens are used for securing the communication between a
    :class:`Source` and a receiver.

    Currently tokens are provided as key files which can be downloaded
    from `Cobe <https://cobe.io/topologies>`_. The :meth:`from_key_files`
    class method should be used to load the key files from a known
    location. This class *should not* be instantiated directly.

    .. warning::
        Keep your authentication tokens safe. Ensure the key files are
        stored securely, with appropriate permissions set.
    """

    def __init__(self, public, private, receiver):
        self._public = public
        self._private = private
        self._receiver = receiver

    @classmethod
    def from_key_files(cls, source, receiver):
        """Create a token from secret and public key files.

        :param source: The path to the secret key file which identifies
            the source.
        :type source: str or pathlib.Path
        :param receiver: The path to the public key file which identifies
            the receiver.
        :type receiver: str or pathlib.Path

        :returns: A new instance of :class:`Token` using the keys
            provided by the key files for the source and receiver.

        :raises TokenError: If the token cannot be loaded from the given
            key files.
        """
        source = pathlib.Path(source)
        receiver = pathlib.Path(receiver)
        try:
            public, private = zmq.auth.load_certificate(str(source))
        except ValueError as exc:
            raise TokenError(
                'Source key file is missing a public key') from exc
        if private is None:
            raise TokenError('Source key file is missing a private key')
        try:
            receiver_public, receiver_private = \
                zmq.auth.load_certificate(str(receiver))
        except ValueError as exc:
            raise TokenError(
                'Receiver key file is missing a public key') from exc
        if receiver_private is not None:
            warnings.warn('Receiver key file contained a private '
                          'key; might have the two key files mixed up')
        return cls(public, private, receiver_public)

    def authenticate(self, socket):
        """Apply the token to a ZeroMQ socket.

        This will apply the appropriate configuration to a given ZeroMQ
        socket so that it uses the authentication credentials as dictated
        by the token.
        """
        socket.CURVE_PUBLICKEY = self._public
        socket.CURVE_SECRETKEY = self._private
        socket.CURVE_SERVERKEY = self._receiver


class Source:
    """Implements a Streaming API source.

    A source is responsible for communicating with a Streaming API receiver
    over a ZeroMQ socket secured by an authentication :class:`Token`.

    :param destination: The ZeroMQ endpoint of the Streaming API receiver.
    :type destination: str
    :param token: An authentication token to use for securing updates sent
        to the receiver.
    :type token: cobe.Token

    :raises SourceError: If an invalid destination is given.
    """

    def __init__(self, *, destination, token):
        self._opened = False
        self._closed = False
        self._destination = self._normalise_destination(destination)
        self._token = token
        self._context = None
        self._socket = None

    def __enter__(self):
        """Enter the context manager for the source.

        This will ensure the connection to receiver is made.

        :raises SourceError: If the source has already been closed.

        :returns The :class:`Source` instance.
        """
        self.open()
        return self

    def __exit__(self, exception, type_, traceback):
        """Exit the source context manager.

        This will flush any buffers and then finally close the connection
        to the receiver. See :meth:`close`.
        """
        self.close()

    def _normalise_destination(self, destination):
        """Normalise a ZMQ endpoint.

        This will ensure the given ZMQ endpoint has a scheme as well as
        a port. Only ``tcp:`` schemes are valid and if no scheme is given
        it will default to ``tcp:``.

        The default port is 25010.

        :param destination: The ZMQ endpoint to normalise.
        :type destination: str

        :returns: A string containing the normalised ZMQ endpoint.

        :raises SourceError: If the destination cannot be normalised.
            E.g. an empty string is given or contains an invalid scheme.
        """
        url = urllib.parse.urlparse(destination)
        scheme = url.scheme
        authority = url.netloc
        path = url.path
        if not scheme:
            scheme = 'tcp'
        if scheme == 'tcp':
            if not authority and path:
                authority = path
                path = ''
            ipv6 = '[' in authority and ']' in authority
            if ipv6:
                maybe_host = authority[:authority.find(']') + 1]
                maybe_port = authority[authority.find(']') + 2:]
                host_and_port = [maybe_host]
                if maybe_port:
                    host_and_port.append(maybe_port)
            else:
                host_and_port = authority.rsplit(':', 1)
            if len(host_and_port) == 2:
                host, port = host_and_port
            else:
                host = host_and_port[0]
                port = '25010'
            if not host:
                raise SourceError('Destination host must be given with tcp:')
            try:
                port_numeric = int(port)
            except ValueError as exc:
                raise SourceError(
                    'Destination port must be an integer') from ValueError
            authority = host + ':' + port
            if path:
                raise SourceError('Destination cannot have a path with tcp:')
        else:
            raise SourceError("Source destination scheme must be tcp:")
        return scheme + '://' + authority + path

    @property
    def destination(self):
        """Get the normalised destination endpoint address."""
        return self._destination

    def open(self):
        """Open a connection to the receiver.

        To clean up the resources that are created this method :meth:`close`
        must be called. Alternatively, a :class:`Source` can be used as a
        context manager which will handle the clean up automatically.

        :raises SourceError: If the source has been already opened or closed.
        """
        if self._opened:
            raise SourceError('Source already open')
        if self._closed:
            raise SourceError('Source closed')
        self._context = zmq.Context()
        self._context.IPV6 = True
        self._context.LINGER = 500
        self._socket = self._context.socket(zmq.PUSH)
        self._token.authenticate(self._socket)
        self._socket.connect(self._destination)
        self._opened = True


    def close(self):
        """Flush buffers and close the connection.

        Once called the :class:`Source` cannot be reused for sending
        additional updates. Any attempt to do so will result in a
        :exc:`SourceError` being raised.

        It is always safe to call this method.

        .. note::
            It's advisable to use a source as a context manager which will
            automatically handle closing of the connection:

            .. code-block:: python

                with cobe.Source(destination=..., token=...) as source:
                    source.send(...)
        """
        self._opened = False
        self._closed = True
        if self._socket:
            self._socket.close(linger=500)
        if self._context:
            self._context.term()
        self._socket = None  # Guard against programming errors
        self._context = None

    def send(self, model):
        """Send a model to the receiver.

        This serialises a given model and sends it to the connected
        Streaming API receiver.

        :param model: The model to send.
        :type mode: cobe.Model

        :raises SourceError: If the source is not open or has been closed,
            or the receiver is not accepting the updates, e.g. due to the
            destination or authentication token being wrong.
        :raises ProtocolError: If the given model contains entities that
            cannot be serialised as a valid Streaming API update message.
            Note that when this is raised, no updates from the model will
            be sent at all.
        :raises cobe.ModelError: If the given model contains invalid
            relationships or non-:class:`Update`s.
        """
        if self._closed:
            raise SourceError('Source closed')
        if not self._opened:
            raise SourceError('Source not open')
        messages = []
        model.validate()
        for entity, parents, children in model:
            messages = []
            message = {
                'ueid': entity,
                'exists': entity.exists,
                'type': entity.type,
                'attrs': entity.attributes,
                'parents': parents,
                'children': children,
            }
            if entity.timestamp is not None:
                message['timestamp'] = entity.timestamp
            if entity.label is not None:
                message['label'] = entity.label
            if entity.ttl is not None:
                message['ttl'] = entity.ttl
            try:
                messages.append(_SCHEMA_UPDATE(message))
            except voluptuous.Invalid as exc:
                raise ProtocolError('Could not construct '
                                    'entity update: {}'.format(exc)) from exc
            self._dispatch_messages(messages)

    def _dispatch_messages(self, messages):
        """Serialise and send messages to the receiver.

        This will serialise the given messages as MessagePack and send them
        over the connected ZeroMQ socket. If any of the messages cannot be
        serialised then none of them are sent.

        :param messages: An iterable of serialisable entity update messages.

        :raises ProtocolError: If any of the given messages cannot be
            serialised as MessagePack.
        :raises SourceError: If the send buffer is full.
        """
        serialised = []
        for message in messages:
            try:
                serialised.append(msgpack.packb(message, use_bin_type=True))
            except TypeError as exc:
                raise ProtocolError(
                    'Cannot serialise message {!r}'.format(message)) from exc
        for serialised_message in serialised:
            frames = (_PROTOCOL_VERSION, serialised_message)
            try:
                self._socket.send_multipart(frames, flags=zmq.DONTWAIT)
            except zmq.Again as exc:
                raise SourceError('Send buffer full') from exc
