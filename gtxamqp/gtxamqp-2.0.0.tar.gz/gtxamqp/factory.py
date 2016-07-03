import os

from twisted.internet import protocol, reactor
from twisted.internet.defer import Deferred, inlineCallbacks, passthru, DeferredList
from twisted.internet.task import deferLater
from txamqp import spec
from txamqp.client import TwistedDelegate

from gtxamqp.facade import AmqpClient
from protocol import AmqpProtocol


class AmqpReconnectingFactory(protocol.ReconnectingClientFactory):
    protocol = AmqpProtocol

    def __init__(self, spec_file=None,
                 host='localhost', port=5672, user="guest",
                 prefetch=10,
                 password="guest", vhost="/",
                 post_teardown_func=None):
        spec_file = spec_file or os.path.join(os.path.dirname(__file__), 'amqp0-8.stripped.rabbitmq.xml')
        self.spec = spec.load(spec_file)
        self.user = user
        self.password = password
        self.vhost = vhost
        self.host = host
        self.prefetch = prefetch
        self.delegate = TwistedDelegate()
        self.deferred = Deferred()
        self.post_teardown_func = post_teardown_func
        self.clients = {}
        self.unused_client_ids = []
        self.p = None  # The protocol instance.
        self._consumers = {}
        self.connector = reactor.connectTCP(self.host, port, self)

    def get_client(self, queue=None, exchange=None, binding=None):
        # clients are zero based, channels start at 1
        client_spot = self._next_client_spot()
        client = AmqpClient(factory=self,
                            channel_id=client_spot + 1,
                            queue=queue,
                            binding=binding,
                            exchange=exchange,
                            teardown_func=self._remove_client)
        self.clients[client_spot] = client
        return client

    def _remove_client(self, client):
        # channel id's start at 1, while clients start at zero
        client_id = client.channel_id - 1
        if client_id in self.clients:
            self.unused_client_ids.append(client_id)
            # instead of deleting items, we rehash the dict
            self.clients = {cid: c for cid, c in self.clients.items() if cid != client_id}

    def _next_client_spot(self):
        if self.unused_client_ids:
            return self.unused_client_ids.pop()
        return len(self.clients)

    def _start_consumers(self):
        dl = []
        for consumer, client in self._consumers.itervalues():
            dl.append(client.basic_consume(**consumer.conf))
        self._consumers = {}
        return DeferredList(dl)

    def _stop_consumers(self):
        for consumer, _ in self._consumers.values():
            consumer.stop()

    def add_consumer(self, client, consumer):
        self._consumers[consumer.consumer_tag] = (consumer, client)
        return consumer

    def remove_consumer(self, consumer_tag):
        if consumer_tag not in self._consumers:
            return

        consumer, client = self._consumers.pop(consumer_tag)
        return consumer

    def get_consumer_by_tag(self, consumer_tag):
        if consumer_tag not in self._consumers:
            return
        consumer, _ = self._consumers[consumer_tag]
        return consumer

    def _reconnect_on_fail(self, failure):
        if self.p:
            self.p.transport.loseConnection()
        self.p = None
        return failure

    def _get_call_deferred(self, method_name, *args, **kwargs):
        channel_id = kwargs.pop("channel_id", None)
        if channel_id:
            kwargs["channel"] = self.p.channels[channel_id]

        d = getattr(self.p, method_name)(*args, **kwargs)
        d.addErrback(self._reconnect_on_fail)
        return d

    def call_method(self, method_name, *args, **kwargs):
        if self.p and self.p.connected:
            return self._get_call_deferred(method_name, *args, **kwargs)

        if not self.deferred:
            self.deferred = Deferred()

        self.deferred.addCallback(lambda *x: self.call_method(method_name, *args, **kwargs))
        return self.deferred

    def buildProtocol(self, addr):
        self.p = self.protocol(factory=self,
                               delegate=self.delegate,
                               vhost=self.vhost,
                               spec=self.spec)
        reactor.callLater(0, self._start_consumers)
        self.resetDelay()
        return self.p

    def startedConnecting(self, connector):

        @inlineCallbacks
        def resume_clients(*x):
            for c in self.clients.values():
                yield c.resume()

        # add initialize clients at the beginning
        # of the chain, to make sure everything is resumed
        # before firing all deferreds

        cbs = ((resume_clients, [], {}), (passthru, None, None))
        self.deferred.callbacks.insert(0, cbs)

        protocol.ReconnectingClientFactory.startedConnecting(self, connector)

    def clientConnectionFailed(self, connector, reason):
        self.p = None
        protocol.ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionLost(self, connector, reason):
        self._stop_consumers()
        self.p = None
        protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

    def retry(self, connector=None):
        if self.deferred.called:
            self.deferred = Deferred()

        protocol.ReconnectingClientFactory.retry(self, connector)

    @inlineCallbacks
    def teardown(self, *args):
        """
        close the factory gracefully.
        does not close before a connection has been made
        """
        deferred = deferLater(reactor, 0, lambda *x: None)
        if self.continueTrying and not self.deferred.called:
            self.deferred.addCallback(self.teardown)
            deferred = self.deferred
        else:
            self.stopTrying()
            self.connector.disconnect()
            if self.p and self.p.connected:
                deferred = self.p.onConnectionLost

            for c in self.clients.values():
                yield c.teardown()

            if self.post_teardown_func:
                deferred.addBoth(lambda *a, **kw: self.post_teardown_func(self))

        yield deferred
