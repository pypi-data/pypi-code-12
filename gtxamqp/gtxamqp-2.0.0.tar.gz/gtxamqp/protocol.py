import random

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, Deferred
from txamqp.content import Content
from txamqp.protocol import AMQClient

from gtxamqp.consumer import Consumer


class AmqpProtocol(AMQClient):
    """
    The protocol is created and destroyed each time a connection is created and lost.
    """

    def __init__(self, delegate, vhost, spec, factory):
        AMQClient.__init__(self, delegate, vhost, spec)
        self.factory = factory
        self.onConnectionLost = Deferred()

    def get_random_channel(self):
        """
        returns a random, opened channel
        :return:
        """
        if len(self.factory.clients) == 1:
            # only using channel 1, not channel 0
            return self.channels[1]

        channels = [c for cid, c in self.channels.items() if cid > 0 and hasattr(c, "initialized")]
        # choose an open channel if possible,
        # otherwise, randomly choose a closed one
        channel = random.choice(channels) if channels \
            else random.choice(self.channels.values())
        return channel

    @inlineCallbacks
    def close_channel(self, channel_id, reason=None):
        """
        close a given channel id
        """
        try:
            yield self.channelLock.acquire()
            if channel_id in self.channels:
                ch = self.channels[channel_id]
                if not ch.closed:
                    ch.close(reason or "user")
                del self.channels[channel_id]
        finally:
            self.channelLock.release()

    def connectionMade(self):
        """
        Called when a connection has been made.
        """
        AMQClient.connectionMade(self)

        self.connected = False
        d = self.start({"LOGIN": self.factory.user, "PASSWORD": self.factory.password})
        d.addCallback(self._authenticated)
        d.addErrback(self._authentication_failed)

    def connectionLost(self, reason):
        AMQClient.connectionLost(self, reason)
        self.onConnectionLost.callback(None)

    def _authenticated(self, ignore):
        """
        Called when the connection has been authenticated.
        """
        # used for internal connection pool
        if not self.connected:
            self.connected = True
            reactor.callLater(0, self.factory.deferred.callback, None)

    def _channel_open_failed(self, error):
        pass

    def _authentication_failed(self, error):
        self.factory.deferred.errback(error)

    def basic_get(self, channel, queue, no_ack):
        return channel.basic_get(queue=queue, no_ack=no_ack)

    def basic_publish(self, channel, exchange, msg, routing_key, properties):
        return channel.basic_publish(exchange=exchange,
                                     routing_key=routing_key or '',
                                     content=Content(msg, properties=properties))

    def basic_qos(self, channel, prefetch_count=1):
        return channel.basic_qos(prefetch_count=prefetch_count)

    def basic_consume(self, channel, callback, queue, no_ack, interval=0, consumer_tag=None):
        consumer = Consumer(factory=self.factory,
                            channel_id=channel.id,
                            callback=callback,
                            queue_name=queue,
                            no_ack=no_ack,
                            consumer_tag=consumer_tag)

        return consumer.start(interval).addCallback(lambda *x: consumer)

    @inlineCallbacks
    def basic_cancel(self, channel, consumer):
        yield consumer.stop()
        yield channel.basic_cancel(consumer.consumer_tag)

    def basic_ack(self, channel, delivery_tag):
        return channel.basic_ack(delivery_tag=delivery_tag)

    def basic_recover(self, channel):
        return channel.basic_recover(requeue=True)

    def basic_reject(self, channel, delivery_tag, requeue=False):
        return channel.basic_reject(delivery_tag=delivery_tag, requeue=requeue)

    def queue_declare(self, channel, queue):
        return channel.queue_declare(**queue)

    def queue_delete(self, channel, queue):
        return channel.queue_delete(queue=queue)

    def exchange_declare(self, channel, exchange):
        return channel.exchange_declare(**exchange)

    def exchange_delete(self, channel, exchange):
        return channel.exchange_delete(exchange=exchange)
