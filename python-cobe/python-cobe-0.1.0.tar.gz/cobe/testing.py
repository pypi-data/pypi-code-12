"""Utilities for testing entity update sources."""

import collections
import time

import msgpack
import zmq.auth.thread

import cobe.model
import cobe.ueid
import cobe.source


class ReceiverError(Exception):
    """Base exception raised for all test receiver errors."""


class TimeoutError(Exception):  # TODO: Redefining built-in
    """Raised for timeouts when waiting on expected items.

    The :attr:`partial` attribute's type matches the return type of
    the method that raised the exception. See :meth:`Receiver.expect_raw`
    and :meth:`Receiver.expect`.

    :ivar int count_expected: The number of updates that were expected.
    :ivar int count_received: The number of updates that were received.
    :ivar partial: The partial response that was received before the
        timeout was reached.
    :ivar float elapsed: The number of seconds that passed before the
        timeout was reached.
    """

    def __init__(self, count_expected, partial, elapsed):
        self.count_expected = count_expected
        self.count_received = len(partial)
        self.partial = partial
        self.elapsed = elapsed

    def __str__(self):
        return ('Expected {0.count_expected} but received '
                '{0.count_received} in {0.elapsed:.2f} seconds'.format(self))


class Receiver:
    """Streaming API receiver suitable for testing against."""

    _KEY_RECEIVER_PUBLIC = b'f=RJl!6Psg6&)jbsw>uO/>l>!QLS/[@ve+d0-MZQ'
    _KEY_RECEIVER_PRIVATE = b'x2b7p}.nwn-IeiVT<{:6Ax)BuLK7-[+c=IBy)gDx'
    _KEY_SOURCE_PUBLIC = b'f=RJl!6Psg6&)jbsw>uO/>l>!QLS/[@ve+d0-MZQ'
    _KEY_SOURCE_PRIVATE = b'x2b7p}.nwn-IeiVT<{:6Ax)BuLK7-[+c=IBy)gDx'

    def __init__(self):
        self._closed = False
        self._opened = False
        self._context = None
        self._socket = None
        self._authenticator = None
        self._destination = None

    def __enter__(self):
        """Open the receiver.

        See :meth:`open`.

        :returns: The :class:`Receiver` instance being entered.
        """
        self.open()
        return self

    def __exit__(self, exception, type_, traceback):
        """Close the receiver.

        See :meth:`close`.
        """
        self.close()

    @property
    def destination(self):
        """Get the endpoint address the receiver listens on.

        This can only be accessed once the receiver is open.

        :raises ReceiverError: If accessed before :meth:`open` is called
            or after :meth:`close`.
        """
        if self._closed:
            raise ReceiverError('Receiver is closed')
        if not self._opened:
            raise ReceiverError('Receiver is not open')
        return self._destination

    @property
    def token(self):
        """Get the source authentication token for this receiver.

        This can only be accessed once the receiver is open.

        :raises ReceiverError: If accessed before :meth:`open` is called
            or after :meth:`close`.
        """
        if self._closed:
            raise ReceiverError('Receiver is closed')
        if not self._opened:
            raise ReceiverError('Receiver is not open')
        return cobe.source.Token(
            self._KEY_SOURCE_PUBLIC,
            self._KEY_SOURCE_PRIVATE,
            self._KEY_RECEIVER_PUBLIC,
        )

    def open(self):
        """Open the receiver so that it can start receiving updates.

        This will attempt to bind to a random, high-order port on 127.0.0.1.

        To clean up the resources that are created this method :meth:`close`
        must be called. Alternatively, a :class:`Receiver` can be used
        as a context manager which will handle the clean up automatically.

        If, for whatever reason, the receiver cannot be opened, a
        :exc:`ReceiverError` will be raised and the receiver is closed
        as per :meth:`close`.

        :raises ReceiverError: If a free port to bind to cannot be found
            or any other error that prevents the receiver from starting.
        """
        if self._closed:
            raise ReceiverError('Receiver closed')
        self._context = zmq.Context()
        self._authenticator = \
            zmq.auth.thread.ThreadAuthenticator(self._context)
        self._authenticator.start()
        self._authenticator.thread.authenticator.certs['*'] = {}
        self._authenticator.thread.authenticator.certs[
            '*'][self._KEY_SOURCE_PUBLIC] = True
        self._context.IPV6 = True
        self._context.LINGER = 500
        self._socket = self._context.socket(zmq.PULL)
        self._socket.CURVE_PUBLICKEY = self._KEY_RECEIVER_PUBLIC
        self._socket.CURVE_SECRETKEY = self._KEY_RECEIVER_PRIVATE
        self._socket.CURVE_SERVER = True
        try:
            self._socket.bind('tcp://127.0.0.1:0')
        except zmq.ZMQError as exc:
            self.close()
            if exc.errno == zmq.EADDRINUSE:
                raise ReceiverError('Could not find free port') from exc
            raise ReceiverError(str(exc)) from exc
        else:
            self._destination = self._socket.LAST_ENDPOINT.decode()
        self._opened = True

    def close(self):
        """Close the receiver for new updates.

        Once called the :class:`Receiver` will not be able to
        receiver any more updates. Any attempt to do so will result
        in a :exc:`ReceiverError` being raised.

        .. note::
            It's advisable to use a test receiver as a context manager
            which will automatically handle calling this method:

            .. code-block:: python

                with cobe.testing.Receiver() as receiver:
                    model = receiver.expect(...)
        """
        self._closed = True
        self._opened = False
        if self._authenticator:
            self._authenticator.stop()
        if self._socket:
            self._socket.close(linger=500)
        if self._context:
            self._context.term()
        self._socket = None
        self._context = None
        self._destination = None

    def expect_raw(self, count=1, timeout=1.0):
        """Expect a number of raw messages from a source.

        This method will block waiting for data to be sent from a
        source. The raw data is left as received therefore it is
        advisable to use :meth:`expect` instead.

        :param count: The number of raw messages to expect from the
            source.
        :type count: int
        :param timeout: The maximum number of seconds to wait for the
            messages.
        :type timeout: int or float

        :returns: A tuple containing the received messages. Each message
            is a tuple of byte-strings.

        :raises TimeoutError: If the timeout is reached before ``count``
            messages are received.
        """
        messages = []  # [(frame[, frame ..]), ...]
        deadline = time.monotonic() + timeout
        while len(messages) < count and time.monotonic() < deadline:
            if self._socket.poll(0.5 * timeout * 1000):
                messages.append(tuple(self._socket.recv_multipart()))
        messages_final = tuple(messages)
        if len(messages) < count:
            raise TimeoutError(count, messages_final, timeout)
        return messages_final

    def expect(self, count=1, timeout=1.0):
        """Expect a number of updates from a source.

        This method will block, waiting for updates to be sent from a
        source. The updates will be decoded and used to reconstruct a
        :class:`cobe.Model` that can be inspected.

        The timeout dictates the maximum ammount of time to wait, in
        seconds, for the specified number of updates to be received.

        When sending an update which is related to an
        :class:`cobe.Identifier`, is will appear in the reconstructed
        model as an equivalent :class:`cobe.UEID`. However, the sent
        attributes of the sent identifier cannot be inspected.

        :param count: The number of updates to expect from the source.
        :type count: int
        :param timeout: The maximum number of seconds to wait for upates.
        :type timeout: int or float

        :returns: A :class:`cobe.Model` containing the updates that were
            received.

        :raises TimeoutError: If the timeout is reached before ``count``
            updates are received.
        """
        try:
            messages = self.expect_raw(count, timeout)
        except TimeoutError as exc:
            messages = exc.partial
        model = cobe.model.Model()
        updates = collections.OrderedDict()  # UEID : (dict, Update)
        for _, serialised in messages:
            update_raw = msgpack.unpackb(serialised, encoding='utf-8')
            update = self._update_from_dict(update_raw)
            updates[update.ueid()] = (update_raw, update)
        for update_raw, update in updates.values():
            model.add(update)
            for relationship in ('parents', 'children'):
                for relationship_ueid in update_raw[relationship]:
                    ueid = cobe.ueid.UEID(relationship_ueid)
                    try:
                        relative = updates[ueid][1]
                    except KeyError:
                        relative = ueid
                    if relationship == 'parents':
                        model.relate(parent=relative, child=update)
                    else:
                        model.relate(parent=update, child=relative)
        if len(model) < count:
            raise TimeoutError(count, model, timeout)
        return model

    def _update_from_dict(self, dictionary):
        """Convert a dictionary into an entity update.

        This takes a dictionary as serialised and sent by :class:`Source`
        and turns it back into a :class:`Update`.

        :returns: A :class:`Update` built from the given dictionary.
        """
        update = cobe.model.Update(dictionary['type'])
        if 'label' in dictionary:
            update.label = dictionary['label']
        if 'timestamp' in dictionary:
            update.timestamp = dictionary['timestamp']
        if 'ttl' in dictionary:
            update.ttl = dictionary['ttl']
        for name, attribute in dictionary['attrs'].items():
            if attribute['deleted']:
                update.attributes[name].delete()
            else:
                update.attributes[name].set(attribute['value'])
                update.attributes[name].traits = set(attribute['traits'])
        return update
