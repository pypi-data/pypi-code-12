# -*- encoding: utf-8 -*-

import asyncio

from xbus.broker.core.back.node import WorkerNode
from xbus.broker.core.back.node import ConsumerNode
from xbus.broker.core.back.recipient import Recipient

__author__ = 'faide'


class Event(object):
    """An Event instance represents the event datastructure that is manipulated
    by the backend and dispatched to all workers and consumers that need it"""

    def __init__(
        self, envelope_id: str, event_id: str, type_name: str, type_id: str,
        redis_pool=None, loop=None
    ):
        """Create a new event instance that will be manipulated by the backend,
        it provides a few helper methods and some interesting attributes like
        the event type name and event type id.

        :param envelope_id:
         the UUID of the envelope that contains the event

        :param event_id:
         the generated UUID of the event

        :param type_id:
         the internal UUID that corresponds to the type of the event

        :param type_name:
         the name of the type of the started event

        :param redis_pool:
         the redis connection pool.

        :param loop:
         the event loop used by the backend

        """
        self.envelope_id = envelope_id
        self.event_id = event_id
        self.type_name = type_name
        self.type_id = type_id
        self.nodes = {}
        self.start = []
        self.partial = False
        self.redis_pool = redis_pool
        self.loop = loop

    @asyncio.coroutine
    def new_worker(
        self, node_id, recipient: Recipient, children, is_start
    ):
        """Create a new :class:`.WorkerNode` instance and add it to the event.

        :param node_id:
         the UUID of the worker node

        :param recipient:
         Information about the worker.

        :param children:
         the UUIDs of the children nodes.

        :param is_start:
         True if the node has no parent node, false otherwise.
        """
        try:
            yield from recipient.ping()
        except asyncio.CancelledError:
            return node_id, None, [recipient]
        node = WorkerNode(
            self.envelope_id, self.event_id, node_id, recipient, children,
            self.redis_pool, self.loop
        )
        self._add_node(node, is_start)
        return node_id, node, []

    @asyncio.coroutine
    def new_consumer(self, node_id, recipients: list, is_start):
        """Create a new :class:`.ConsumerNode` instance and add it to the
        event.

        :param node_id:
         the UUID of the consumer node

        :param recipients:
         Information about the consumers.
        :type recipients: List of Recipient objects.

        :param is_start:
         True if the node has no parent node, false otherwise.
        """

        futures = (
            asyncio.async(recipient.ping(), loop=self.loop)
            for recipient in recipients
        )
        try:
            yield from asyncio.gather(*futures, loop=self.loop)
            active = recipients
        except asyncio.CancelledError:
            active = [future.result() for future in futures if future.done()]
        unavailable = (
            [] if len(active) == len(recipients)
            else list(set(recipients) - set(active))
        )

        node = ConsumerNode(
            self.envelope_id, self.event_id, node_id, active,
            self.redis_pool, self.loop
        )
        self._add_node(node, is_start)
        return node_id, node, unavailable

    def _add_node(self, node, is_start):
        """Add a node to the graph of the event.
        """
        self.nodes[node.node_id] = node
        if is_start:
            self.start.append(node)

    def __getitem__(self, key):
        return self.nodes[key]
