import json
import logging
import uuid

import amqp

logger = logging.getLogger(__name__)


class Client(object):
    def __init__(self, name='', prefix='ws', host='localhost', user='guest', password='guest', vhost='/', timeout=5,
                 dumper=None, exchange_type='topic'):
        if not prefix.endswith('_'):
            prefix += '_'
        if len(name) > 0 and not name.endswith('_'):
            name += '_'
        self.credentials = {
            'host': host,
            'userid': user,
            'password': password,
            'virtual_host': vhost
        }
        if dumper is None:
            dumper = json
        self.dumper = dumper
        self.timeout = timeout
        self.prefix = prefix
        self.name = name
        self.exchange_name = self.prefix + 'exchange_' + exchange_type
        self.exchange_type = exchange_type
        self.connection = None
        self.channel = None
        self.connect()

    def connect(self):
        self.connection = amqp.Connection(**self.credentials)
        self.channel = self.connection.channel()

    def close(self):
        self.channel.close()
        # self.connection.close()

    def call(self, key, *args, **kwargs):
        correlation_id = str(uuid.uuid4())
        reply = self.channel.queue_declare(exclusive=True).queue
        routing_key = (self.prefix + self.name).replace('_', '.') + key
        body = self.dumper.dumps({'args': args, 'kwargs': kwargs})
        self.channel.basic_publish(
            amqp.Message(body, reply_to=reply, correlation_id=correlation_id),
            self.exchange_name, routing_key=routing_key,

        )
        logger.debug('Message %s with routing key %s published', body, routing_key)
        logger.debug('Waiting for reply in queue %s with correlation id %s', reply, correlation_id)

        message = {}

        def _reply(_message):
            logger.debug(
                'Reply %s with correlation id %s received', _message.body, _message.properties['correlation_id']
            )
            if _message.properties['correlation_id'] == correlation_id:
                message['result'] = self.dumper.loads(_message.body)
                self.channel.basic_ack(_message.delivery_tag)

        while True:
            self.channel.basic_consume(reply, callback=_reply)
            self.connection.drain_events(self.timeout)
            if 'result' in message:
                return message['result']

    def publish(self, _name, *args, **kwargs):
        routing_key = (self.prefix + self.name + _name).replace('_', '.')
        body = self.dumper.dumps({'args': args, 'kwargs': kwargs})
        self.channel.basic_publish(amqp.Message(body), self.exchange_name, routing_key=routing_key)
        logger.debug('Message %s with routing key %s published', body, routing_key)
