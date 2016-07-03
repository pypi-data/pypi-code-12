import logging
from functools import partial

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, Deferred


def get_exchange_name(exchange=None):
    """
    fetches the exchange name from an exchange config or string
    """
    if not exchange:
        raise ValueError("operation impossible - exchange is not defined!")

    return exchange if isinstance(exchange, basestring) else exchange["exchange"]


def get_queue_name(queue=None):
    """
    fetches the queue name from a queue config or string
    """
    if not queue:
        raise ValueError("operation impossible - queue is not defined!")

    return queue if isinstance(queue, basestring) else queue["queue"]


class ClientError(Exception):
    pass


class AmqpClient(object):
    def __init__(self, factory, channel_id, queue=None, exchange=None, binding=None, prefetch=100, teardown_func=None):
        """
        Initialize an AmqpClient.
        It's considered best practice to avoid initializing clients by yourself,
        and use the AmqpReconnectingFactory.get_client() method instead.
        :param factory: a instance of {gtxamqp.factory.AmqpReconnectingFactory}
        :param channel_id: a channel id that belongs to this client
        :param queue: a queue this client should create and bind to the given exchange
        :param exchange: an exchange that messages will be sent to
        :param binding: the queue bindings to create
        :param prefetch: the prefetch count
        :param teardown_func: a function that will be called post teardown
        """
        self.factory = factory
        self.queue = queue
        self.channel_id = channel_id
        self.bindings = filter(None, binding if isinstance(binding, list) else [binding])
        self.exchange = exchange
        self.deferred = Deferred()
        self.setup_finished = None
        self.prefetch_count = prefetch
        self.teardown_func = teardown_func
        self.paused = False
        self.closed = False
        self.logger = logging.getLogger(__name__)

    def get_channel(self):
        """
        returns a Deferred that will be fired once a channel is ready
        """
        get_channel = Deferred()
        channel_id = self.channel_id

        @inlineCallbacks
        def open_channel():
            try:
                chan = yield self.factory.p.channel(channel_id)
                if not hasattr(chan, "initialized"):
                    chan.initialized = False
                    chan.id = channel_id
                    yield chan.channel_open()
                    chan.initialized = True
                elif not chan.initialized:
                    reactor.callLater(0, open_channel)
                    return
                get_channel.callback(chan)
            except Exception as e:
                get_channel.errback(e)

        reactor.callLater(0, open_channel)
        return get_channel

    @inlineCallbacks
    def setup(self):
        """
        performs all setup stages:
        - create a channel
        - declare the exchange (if it was set)
        - declare the queue (if it was set)
            - including queue bindings
        - setup the channel qos

        if the factory stopped, or the client stopped / paused - the setup halts.
        """
        if self.closed or self.paused or not self.factory.continueTrying:
            self.setup_finished.callback(False)
            return

        try:
            channel = yield self.get_channel()
            if self.exchange:
                yield channel.exchange_declare(**self.exchange)
            if self.queue:
                yield channel.queue_declare(**self.queue)
                for binding in self.bindings:
                    if 'queue' not in binding:
                        binding['queue'] = self.queue['queue']
                    yield channel.queue_bind(**binding)
            yield channel.basic_qos(prefetch_count=self.prefetch_count)
            if not (self.factory.p and self.factory.p.connected and not self.closed and not self.paused):
                raise IOError("we're closed or protocol not ready")
            self.deferred.callback(None)
            self.setup_finished.callback(True)
        except Exception as e:
            reactor.callLater(1, self.setup)

    @inlineCallbacks
    def resume(self):
        """
        resume setting up this channel
        resume has to be called at least once for setup to occur
        """

        # if w'ere closed, don't resume
        # teardown will be waiting on setup_finished
        if self.closed:
            return

        self.paused = True

        if self.setup_finished and not self.setup_finished.called:
            yield self.setup_finished

        self.paused = False

        if self.deferred.called:
            self.deferred = Deferred()
        self.setup_finished = Deferred()
        reactor.callLater(0, self.setup)

        yield self.setup_finished

    @inlineCallbacks
    def teardown(self):
        """
        teardown this client:
            - closes the channel this client uses
            - fires the post teardown function
        """
        self.closed = True

        if self.setup_finished:
            yield self.setup_finished

        if self.factory.p:
            yield self.factory.p.close_channel(channel_id=self.channel_id,
                                               reason="facade teardown")

        if self.teardown_func:
            self.teardown_func(self)

    def __getattr__(self, name):
        """
        looks up attributes in the following order:
            - if the attribute belongs to this client - returns it
            - if the attribute belongs to the factory and can't be re-written - returns it
            - otherwise, re-write the factory method to add the client's channel
        """
        attr = self._safe_get_attribute(name)
        return attr or getattr(self.factory, name)

    def _rewrite_method(self, method_name, **kwargs):
        """
        rewrite an attribute to include all client parameters
        like the queue, exchange, and channel.
        """
        kwargs["channel_id"] = self.channel_id

        if not self.deferred.called:
            self.deferred.addCallback(lambda *x: self._rewrite_method(method_name, **kwargs))
            return self.deferred
        return self.factory.call_method(method_name, **kwargs)

    def _safe_get_attribute(self, name):
        try:
            return self.__getattribute__(name)
        except AttributeError:
            return None

    def basic_get(self, queue=None, no_ack=True):
        """
        Direct access to a queue.

        This method provides a direct access to the messages in a queue using a synchronous dialogue that is
        designed for specific types of application where synchronous functionality is more important than performance.
        """
        queue_name = get_queue_name(queue or self.queue)
        return self._rewrite_method(self.basic_get.func_name,
                                    queue=queue_name,
                                    no_ack=no_ack)

    def basic_qos(self, prefetch_count=100):
        """
        Specify quality of service.

        This method requests a specific quality of service. The QoS can be specified for the current channel or for
        all channels on the connection. The particular properties and semantics of a qos method always depend on the
        content class semantics. Though the qos method could in principle apply to both peers,
        it is currently meaningful only for the server.
        """
        return self._rewrite_method(self.basic_qos.func_name,
                                    prefetch_count=prefetch_count)

    def basic_consume(self, callback, queue=None, no_ack=False, interval=0, consumer_tag=None):
        """
        Start a queue consumer.
        This method asks the server to start a "consumer",
        which is a transient request for messages from a specific queue.
        Consumers last as long as the channel they were declared on, or until the client cancels them.
        """
        queue_name = get_queue_name(queue or self.queue)
        consumer_d = self._rewrite_method(self.basic_consume.func_name,
                                          callback=callback,
                                          queue=queue_name,
                                          no_ack=no_ack,
                                          interval=interval,
                                          consumer_tag=consumer_tag)
        consumer_d.addCallback(lambda c: self.factory.add_consumer(self, c))
        consumer_d.addCallback(lambda c: c.consumer_tag)
        return consumer_d

    def basic_cancel(self, consumer_tag):
        """
        End a queue consumer.

        This method cancels a consumer.
        This does not affect already delivered messages, but it does mean the server will not send any more
        messages for that consumer. The client may receive an arbitrary number of messages, in between sending
        the cancel method and receiving the cancel-ok reply. It may also be sent from the server to the client
        in the event of the consumer being unexpectedly cancelled (i.e. cancelled for any reason other than the
        server receiving the corresponding basic.cancel from the client). This allows clients to be notified of
        the loss of consumers due to events such as queue deletion. Note that as it is not a MUST for clients to
        accept this method from the server, it is advisable for the broker to be able to identify those clients
        that are capable of accepting the method, through some means of capability negotiation.
        """

        d = self._rewrite_method(self.basic_cancel.func_name,
                                 consumer=self.factory.get_consumer_by_tag(consumer_tag))
        d.addCallback(lambda *x: self.factory.remove_consumer(consumer_tag))
        return d

    def basic_publish(self, msg, exchange=None, routing_key='', properties=None):
        """
        Publish a message.

        This method publishes a message to a specific exchange. The message will be routed to queues as defined
        by the exchange configuration and distributed to any active consumers when the transaction, if any, is committed.
        """
        exchange_name = get_exchange_name(exchange or self.exchange)
        return self._rewrite_method(self.basic_publish.func_name,
                                    exchange=exchange_name,
                                    msg=msg,
                                    routing_key=routing_key,
                                    properties=properties)

    def basic_ack(self, delivery_tag):
        """
        Acknowledge one or more messages.

        When sent by the client, this method acknowledges one or more messages delivered via the Deliver or
        Get-Ok methods. When sent by server, this method acknowledges one or more messages published with the
        Publish method on a channel in confirm mode. The acknowledgement can be for a single message or a set
        of messages up to and including a specific message.
        """
        return self._rewrite_method(self.basic_ack.func_name,
                                    delivery_tag=delivery_tag)

    def basic_recover(self):
        """
        Redeliver unacknowledged messages.

        This method asks the server to redeliver all unacknowledged messages on a specified channel.
        Zero or more messages may be redelivered. This method replaces the asynchronous Recover.
        """
        return self._rewrite_method(self.basic_recover.func_name)

    def basic_reject(self, delivery_tag, requeue=False):
        """
        Reject an incoming message.

        This method allows a client to reject a message. It can be used to interrupt and cancel large
        incoming messages, or return untreatable messages to their original queue.
        """
        # for backward compatibility,
        # this method check is msg is a real txamqp.message.Message,
        # if not, fallback to old behaviour where message was a delivery tag
        return self._rewrite_method(self.basic_reject.func_name,
                                    delivery_tag=delivery_tag,
                                    requeue=requeue)

    def queue_declare(self, queue=None):
        """
        Declare queue, create if needed.

        This method creates or checks a queue. When creating a new queue the client can specify various
        properties that control the durability of the queue and its contents, and the level of sharing for the queue.
        RabbitMQ implements extensions to the AMQP specification that permits the creator of a queue to control various
        aspects of its behaviour.
        """
        return self._rewrite_method(self.queue_declare.func_name,
                                    queue=queue or self.queue)

    def queue_delete(self, queue=None):
        """
        Delete a queue.

        This method deletes a queue. When a queue is deleted any pending messages are sent to a dead-letter
        queue if this is defined in the server configuration, and all consumers on the queue are cancelled.
        """
        queue_name = get_queue_name(queue or self.queue)
        return self._rewrite_method(self.queue_delete.func_name,
                                    queue=queue_name)

    def exchange_declare(self, exchange=None):
        """
        Verify exchange exists, create if needed.

        This method creates an exchange if it does not already exist, and if the exchange exists, verifies that it
        is of the correct and expected class.

        RabbitMQ implements an extension to the AMQP specification that allows for unroutable messages to be delivered
        to an Alternate Exchange (AE). The AE feature helps to detect when clients are publishing messages that cannot
        be routed and can provide "or else" routing semantics where some messages are handled specifically and the remainder
        are processed by a generic handler.
        """
        return self._rewrite_method(self.exchange_declare.func_name,
                                    exchange=exchange or self.exchange)

    def exchange_delete(self, exchange=None):
        """
        Delete an exchange.

        This method deletes an exchange. When an exchange is deleted all queue bindings on the exchange are cancelled.
        """
        exchange_name = get_exchange_name(exchange or self.exchange)
        return self._rewrite_method(self.exchange_delete.func_name,
                                    exchange=exchange_name)
