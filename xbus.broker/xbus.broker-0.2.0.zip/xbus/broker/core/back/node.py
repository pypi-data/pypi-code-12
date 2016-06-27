# -*- encoding: utf-8 -*-

import asyncio
import json

from xbus.broker.core.back.recipient import Recipient

__author__ = 'jgavrel'


class Node(object):
    """a Node instance represents one node in the event datastructure that is
    manipulated by the backend."""

    def __init__(
        self, envelope_id, event_id, node_id, redis_pool=None, loop=None
    ):
        """create a new event instance that will be manipulated by the backend,
        it provides a few helper methods and some interesting attributes like
        the event type name and event type id

        :param envelope_id:
         The UUID of then envelope

        :param event_id:
         The UUID of the event

        :param node_id:
         The UUID of the node

        :param redis_pool:
         the redis connection pool.

        :param loop:
         the event loop used by the backend
        """
        self.envelope_id = envelope_id
        self.event_id = event_id
        self.node_id = node_id
        self.redis_pool = redis_pool
        self.loop = loop

        self.sent = 0
        self.recv = 0
        self.queued = True
        self.active = False
        self.done = False
        self.trigger = asyncio.Future(loop=loop)

    @property
    def redis_key(self):
        return 'xbus.broker:node:{}:{}'.format(self.event_id, self.node_id)

    @asyncio.coroutine
    def push_queue(self, indices, data):
        indices_json = json.dumps(indices).encode('utf-8')
        elem = b'\0'.join((indices_json, data))
        with (yield from self.redis_pool) as conn:
            qsize = yield from conn.rpush(self.redis_key, elem)
        return qsize

    @asyncio.coroutine
    def pop_queue(self):
        with (yield from self.redis_pool) as conn:
            elem = yield from conn.lpop(self.redis_key)
        indices_json, data = elem.split(b'\0', 1)
        indices = json.loads(indices_json.decode('utf-8'))
        return indices, data

    @asyncio.coroutine
    def get_queue_size(self):
        with (yield from self.redis_pool) as conn:
            qsize = yield from conn.llen(self.redis_key)
        return qsize

    @asyncio.coroutine
    def cancel_queue(self):
        with (yield from self.redis_pool) as conn:
            yield from conn.delete(self.redis_key)

    @asyncio.coroutine
    def wait_trigger(self, index=0, queued=None) -> bool:
        """A coroutine that waits until the node's recv attribute has reached a
        certain value or until the envelope is cancelled.

        :param index:
         The expected value for the node's recv attribute.
        :param queued:
         Desired queue state.
        :returns:
         True if the value has been reached, False if it has been cancelled.
        """

        while self.recv < index or not (
            queued is None or queued is self.queued
        ):
            trigger_res = yield from self.trigger
            if trigger_res is False:
                return False
        return True

    def next_trigger(self):
        """Increments the recv attribute and causes all pending wait_trigger
        coroutines for this node to reevaluate their condition.
        """

        if self.trigger._callbacks:
            self.trigger.set_result(True)
            self.trigger = asyncio.Future(loop=self.loop)

    def cancel_trigger(self):
        """Cause all pending :meth:`wait_trigger` coroutines to return False.
        """
        self.trigger.set_result(False)


class WorkerNode(Node):

    def __init__(
        self, envelope_id: str, event_id: str, node_id: str,
        recipient: Recipient, children, redis_pool=None, loop=None
    ):
        """Create a new worker node instance

        :param envelope_id:
         the UUID of then envelope

        :param event_id:
         the UUID of the event

        :param node_id:
         the UUID of the node

        :param recipient:
         Information about the worker.

        :param children:
         the UUIDs of the children nodes.

        :param redis_pool:
         the redis connection pool.

        :param loop:
         the event loop used by the backend
        """
        super(WorkerNode, self).__init__(
            envelope_id, event_id, node_id, redis_pool=redis_pool, loop=loop
        )
        self.recipient = recipient
        self.children = children

    @property
    def role_id(self):
        return self.recipient.role_id

    @property
    def recipients(self):
        return [self.recipients]

    @property
    def role_ids(self):
        return [self.role_id]

    @staticmethod
    def is_consumer():
        return False


class ConsumerNode(Node):

    def __init__(
        self, envelope_id: str, event_id: str, node_id: str, recipients: list,
        redis_pool=None, loop=None
    ):
        """create a new consumer node instance

        :param envelope_id:
         the UUID of then envelope

        :param event_id:
         the UUID of the event

        :param node_id:
         the UUID of the node

        :param recipients:
         Information about the consumers.
        :type recipients: List of Recipient objects.

        :param redis_pool:
         the redis connection pool.

        :param loop:
         the event loop used by the backend
        """
        super(ConsumerNode, self).__init__(
            envelope_id, event_id, node_id, redis_pool=redis_pool, loop=loop
        )
        self.recipients = recipients
        self.done = False

    @property
    def role_ids(self):
        return [r.role_id for r in self.recipients]

    @staticmethod
    def is_consumer():
        return True
