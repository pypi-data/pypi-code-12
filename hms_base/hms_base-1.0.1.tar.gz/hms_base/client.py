import logging
import json

import pika

from hms_base.decorators import topic


def get_logger():
    return logging.getLogger(__name__)


class Client:
    """Overlay for easy microservices communication."""

    def __init__(self, name, exchange, topics, enable_ping=True):
        """Initialize the client with connection settings.

        Args:
            name; name of the client
            exchange: name of the exchange to connect to
            topics: list of routing keys to listen to
            enable_ping: enable answering to ping requests

        By default, the 'ping' routing key will be added in order to enable
        response to ping requests expect specified otherwise.

        """
        self.name = name
        self.exchange = exchange
        self.topics = topics
        self.listeners = []

        if enable_ping:
            self.listeners.append(self._handle_ping)
            if 'ping' not in self.topics:
                self.topics.append('ping')

        self._channel = None
        self._conn = None
        self._queue_name = None

    def connect(self, host='localhost'):
        """Connect to the server and set everything up.

        Args:
            host: hostname to connect to

        """

        # Connect

        get_logger().info("Connecting to RabbitMQ server...")

        self._conn = pika.BlockingConnection(
            pika.ConnectionParameters(host=host))
        self._channel = self._conn.channel()

        # Exchanger

        get_logger().info("Declaring direct exchanger {}...".format(
            self.exchange))

        self._channel.exchange_declare(exchange=self.exchange, type='direct')

        # Create queue

        get_logger().info("Creating RabbitMQ queue...")
        result = self._channel.queue_declare(exclusive=True)

        self._queue_name = result.method.queue

        # Binding

        for routing_key in self.topics:
            get_logger().info(
                "Binding queue to exchanger {} with routing key {}...".format(
                    self.exchange, routing_key))

            self._channel.queue_bind(
                exchange=self.exchange,
                queue=self._queue_name,
                routing_key=routing_key)

        # Callback

        get_logger().info("Binding callback...")
        self._channel.basic_consume(
            self._callback, queue=self._queue_name, no_ack=True)

    def publish(self, topic, dct):
        """Send a dict with internal routing key to the exchange.

        Args:
            topic: topic to publish the message to
            dct: dict object to send

        """
        get_logger().info("Publishing message {} on routing key "
                          "{}...".format(dct, topic))

        self._channel.basic_publish(
            exchange=self.exchange,
            routing_key=topic,
            body=json.dumps(dct)
        )

    def start_consuming(self):
        """Start the infinite blocking consume process."""
        get_logger().info("Starting passive consuming...")
        self._channel.start_consuming()

    def stop_consuming(self):
        """Stop the consume process."""
        get_logger().info("Stopping passive consuming...")
        self._channel.stop_consuming()

    def disconnect(self):
        """Disconnect from the RabbitMQ server."""
        get_logger().info("Disconnecting from RabbitMQ server...")
        self._conn.close()

    def _callback(self, ch, method, properties, body):
        """Internal method that will be called when receiving message."""

        get_logger().info("Message received! Calling listeners...")

        topic = method.routing_key
        dct = json.loads(body.decode('utf-8'))

        for listener in self.listeners:
            listener(self, topic, dct)

    @staticmethod
    @topic('ping')
    def _handle_ping(client, topic, dct):
        """Internal method that will be called when receiving ping message."""
        if dct['type'] == 'request':
            resp = {
                'type': 'answer',
                'name': client.name,
                'source': dct
            }

            client.publish('ping', resp)