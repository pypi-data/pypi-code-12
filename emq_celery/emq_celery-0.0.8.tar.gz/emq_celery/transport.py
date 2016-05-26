#!/usr/bin/env python
# -*- coding: utf-8 -*-

from kombu.transport import virtual

from emq.client.clientfactory import ClientFactory
from emq.message.ttypes import SendMessageRequest, ReceiveMessageRequest, DeleteMessageRequest, \
    ChangeMessageVisibilityRequest
from emq.queue.ttypes import GetQueueInfoRequest, QueueAttribute, CreateQueueRequest, DeleteQueueRequest, \
    ListQueueRequest, PurgeQueueRequest
from rpc.auth.ttypes import Credential, UserType

from Queue import Empty

import json, re


class EMQChannel(virtual.Channel):
    queues = {}
    messages = {}
    do_restore = False
    supports_fanout = True
    message_invisible_seconds = 12 * 3600
    message_delay_seconds = 0

    def __init__(self, connection, **kwargs):

        super(EMQChannel, self).__init__(connection, **kwargs)

        if 'visibility_timeout' in connection.client.transport_options:
            self.message_invisible_seconds = connection.client.transport_options["visibility_timeout"]
            if self.message_invisible_seconds > 12 * 3600:
                raise Exception("EMQ visibility_timeout with limit 0 - 12 hours")

        app_key = connection.client.userid
        app_secret = connection.client.password
        endpoint = 'http://' + connection.client.hostname

        credential = Credential(UserType.APP_SECRET, app_key, app_secret)
        client_factory = ClientFactory(credential)
        self.queue_client = client_factory.queue_client(endpoint)
        self.message_client = client_factory.message_client(endpoint)

    def _has_queue(self, queue, **kwargs):
        queue = _format_name(queue)
        return queue in self.queues

    def _new_queue(self, queue, **kwargs):
        queue = _format_name(queue)
        if queue not in self.queues:

            # 在创建queue之前，先判断queue是否已经创建过了
            req = ListQueueRequest(queueNamePrefix=queue)
            res = self.queue_client.listQueue(req)
            if not res.queueName:
                queue_attribute = QueueAttribute()
                create_request = CreateQueueRequest(queueName=queue, queueAttribute=queue_attribute)
                create_queue_response = self.queue_client.createQueue(create_request)
                self.queues[queue] = create_queue_response.queueName
            else:
                self.queues[queue] = res.queueName[0]
            print u'Using Queue[' + self.queues[queue] + ']'

    def _get(self, queue, timeout=None):
        queue = _format_name(queue)
        emq_queue = self.queues[queue]
        req = ReceiveMessageRequest(emq_queue, maxReceiveMessageNumber=1, maxReceiveMessageWaitSeconds=20)
        res = self.message_client.receiveMessage(req)
        if not res:
            raise Empty()
        emq_msg = res[0]
        msg = json.loads(emq_msg.messageBody)

        # 将EMQ的消息与celery的消息做映射
        delivery_tag = msg["properties"]["delivery_tag"]
        self.messages[delivery_tag] = (emq_msg.receiptHandle, emq_queue)

        return msg

    def _queue_for(self, queue):
        queue = _format_name(queue)
        if queue not in self.queues:
            self._new_queue(queue)

        return self.queues[queue]

    def _queue_bind(self, *args):
        pass

    def _put_fanout(self, exchange, message, routing_key=None, **kwargs):
        for queue in self._lookup(exchange, routing_key):
            self._put(queue, message)
            super(EMQChannel, self)._put(queue, message, routing_key=routing_key, **kwargs)

    def _put(self, queue, message, **kwargs):
        queue = _format_name(queue)
        send_message_request = SendMessageRequest(self.queues[queue], json.dumps(message), self.message_delay_seconds,
                                                  self.message_invisible_seconds)
        self.message_client.sendMessage(send_message_request)

    def basic_ack(self, delivery_tag):
        handle, queue = self.messages[delivery_tag]
        req = DeleteMessageRequest(queue, handle)
        self.message_client.deleteMessage(req)
        super(EMQChannel, self).basic_ack(delivery_tag)

    def basic_reject(self, delivery_tag, requeue=False):
        if requeue:
            handle, queue = self.messages[delivery_tag]
            req = ChangeMessageVisibilityRequest(queue, handle, 0)
            self.message_client.changeMessageVisibilitySeconds(req)
        super(EMQChannel, self).basic_reject(delivery_tag, requeue)

    def _restore(self, message):
        pass

    def _size(self, queue):
        queue = _format_name(queue)
        req = GetQueueInfoRequest(self.queues[queue])
        res = self.queue_client.getQueueInfo(req)
        return res.queueState.approximateAvailableMessageNumber

    def _delete(self, queue, *args):
        queue = _format_name(queue)
        req = DeleteQueueRequest(queueName=queue)
        self.queue_client.deleteQueue(req)
        del self.queues[queue]
        super(EMQChannel, self)._delete(queue, *args)

    def _purge(self, queue):
        size = self._size(queue)
        queue = _format_name(queue)
        req = PurgeQueueRequest(queue)
        self.queue_client.purgeQueue(req)
        print u'Purge Queue[' + queue + ']'
        super(EMQChannel, self)._purge(queue)
        return size

    def close(self):
        self.queues = {}
        super(EMQChannel, self).close()
        print u'Close Channel'

    def after_reply_message_received(self, queue):
        pass


class EMQTransport(virtual.Transport):
    Channel = EMQChannel

    #: memory backend state is global.
    state = virtual.BrokerState()

    driver_type = 'emq'
    driver_name = 'emq'

    def driver_version(self):
        return 'N/A'


def _format_name(name):
    """
    格式化celery的quque名称，因为emq对名称有格式限制
    :param name:
    :return:
    """
    name, number = re.subn('[^a-zA-Z0-9_]', '_', name)
    return name
