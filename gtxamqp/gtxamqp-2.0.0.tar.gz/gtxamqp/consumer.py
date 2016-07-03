import logging
import uuid

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import LoopingCall
from txamqp.queue import Empty, Closed

logger = logging.getLogger(__name__)


class MissingProtocol(Exception):
    pass


class Consumer(object):
    def __init__(self, factory, channel_id, queue_name, callback, no_ack=False, consumer_tag=None):
        """
        initializes a consumer
        :param factory: the factory to use in order to create the consumer
        :param channel_id: the channel id of the channel to use
        :param queue_name: the queue name to bind to
        :param callback: a callback to fire once a message exists
        :param consumer_tag: a specific consumer tag to use when creating the consumer
        """
        self.no_ack = no_ack
        self.factory = factory
        self.callback = callback
        self.channel_id = channel_id
        self.consumer_tag = consumer_tag
        self.consumer_queue = None
        self.queue_name = queue_name
        self.consumer = LoopingCall(self.consume_message)

    def __str__(self):
        return "{}-{}".format(hex(id(self)), self.channel_id)

    @property
    def conf(self):
        """
        returns this consumers configuration
        """
        return dict(callback=self.callback,
                    queue=self.queue_name,
                    no_ack=self.no_ack,
                    consumer_tag=self.consumer_tag)

    @inlineCallbacks
    def reset(self):
        """
        restarts the consumer
        :return:
        """
        self.stop()
        self.consumer_queue = None

        yield self.start()

    @property
    def protocol(self):
        """
        returns the factory's protocol
        :return:
        """
        return self.factory.p

    @inlineCallbacks
    def _initialize(self):
        if not self.protocol:
            raise MissingProtocol()
        channel = self.protocol.channels[self.channel_id]
        consumer_tag = self.consumer_tag or "-".join(["gctxqmp.ctag", str(uuid.uuid4())])
        msg = yield channel.basic_consume(queue=self.queue_name, no_ack=self.no_ack, consumer_tag=consumer_tag)
        self.consumer_tag = msg.consumer_tag
        self.consumer_queue = yield self.factory.p.queue(self.consumer_tag)
        if msg.content:
            reactor.callLater(0, self.callback, msg)

    @inlineCallbacks
    def start(self, interval=0):
        """
        start this consumer -
        * initialize the consumer
        * start consuming messages every given interval
        """
        try:
            if not self.consumer_queue:
                yield self._initialize()
            self.consumer.start(interval)
        except Exception as e:
            logger.error("Failed on start consumer %s: %s",
                         str(self),
                         e.message)

    def stop(self):
        """
        stop this consumer
        """
        if self.consumer.running:
            self.consumer.stop()

    def _on_error(self, failure):
        if failure.type is Empty:
            logger.info("Empty consumer queue: %s" % self.consumer_tag)
        elif failure.type is Closed:
            logger.info("Closed consumer queue: %s" % self.consumer_tag)

    def _on_message(self, msg):
        if msg.content:
            msg.__dict__["no_ack"] = self.no_ack
            return msg

    def consume_message(self):
        """
        perform a consume operation
        """
        d = self.consumer_queue.get(timeout=5).addCallback(self._on_message)
        d.addCallback(self.callback)
        d.addErrback(self._on_error)
        return d
