import random
from collections import defaultdict
from copy import copy
from hashlib import sha256
from itertools import chain
from pprint import pformat

from twisted.internet import reactor
from twisted.internet.defer import DeferredList

from gtxamqp.factory import AmqpReconnectingFactory


class AmqpReconnectingFactoryPool(object):
    """
    Each factory creates ONE connection,
    while each connection can have multiple channels
    it is suggested to have one connection and use multiple channels
    that are multiplexed on top of that one connection.

    The pool creates as many connections per host as configured,
    and multiplexes channels on top of the connections given.

    The connections to the host are chosen randomly

    read more here:
        - https://www.rabbitmq.com/tutorials/amqp-concepts.html#Connections
        - https://goo.gl/oGePj5
    """
    _pool = defaultdict(list)
    _lookup_table = {}
    _pool_size = 1

    def __init__(self, pool_size=None):
        if not pool_size:
            return

        self.increase_pool_size(pool_size)

    def increase_pool_size(self, pool_size):
        """
        increase the pool size to a given size
        the size is not the delta to increment, but the absolute pool size
        """
        if pool_size > self._pool_size:
            self._pool_size = pool_size

    def __len__(self):
        """
        return the length of all factories in the pool
        """
        return len(self)

    def __iter__(self):
        """
        return all connections in this pool
        """
        factories = chain(*self._pool.values())
        return factories.__iter__()

    def teardown(self, *x):
        """
        teardown the entire pool - clear all clients and connections
        :param x:
        :return:
        """
        return DeferredList([f.teardown() for f in self])

    def _add_factory(self, factory_hash, factory):
        self._pool[factory_hash].append(factory)
        self._lookup_table[hash(factory)] = factory_hash

    def _remove(self, factory):
        factory_key = hash(factory)
        factory_hash = self._lookup_table.pop(factory_key, None)
        if not factory_hash:
            # probably teardown has been called multiple times
            return
        factories = self._pool.get(factory_hash, [])
        if factory in factories:
            factories.remove(factory)
            if not factories:
                del self._pool[factory_hash]

    def get(self, rabbitmq_conf):
        """
        returns a client initialized to the given configuration
        the client is attached to one of the amqp connections to the given host
        """
        config = copy(rabbitmq_conf)
        exchange = config.pop("exchange", None)
        queue = config.pop("queue", None)
        binding = config.pop("binding", None)

        factory_hash = sha256(pformat(config)).hexdigest()
        for _ in xrange(0, self._pool_size - len(self._pool.get(factory_hash, []))):
            factory = AmqpReconnectingFactory(post_teardown_func=self._remove,
                                              **config)
            self._add_factory(factory_hash, factory)

        factory = random.choice(self._pool[factory_hash])
        return factory.get_client(exchange=exchange,
                                  queue=queue,
                                  binding=binding)


pool = AmqpReconnectingFactoryPool(pool_size=1)
reactor.addSystemEventTrigger("before", "shutdown", pool.teardown)
