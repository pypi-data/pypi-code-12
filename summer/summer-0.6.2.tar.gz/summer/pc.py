# -*- coding: utf-8 -*-
# Time-stamp: < pc.py (2016-02-14 14:49) >

# Copyright (C) 2009-2016 Martin Slouf <martin.slouf@sourceforge.net>
#
# This file is a part of Summer.
#
# Summer is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

"""``pc`` module defines necessary classes for producer-consumer
multi-threaded problem.

Usual use case is to create some kind of (thread-safe) generator (usually
shared by py:class:`Producer` instances).  Obtain single value in
:py:meth:`Producer.produce` (obtaining value must be thread-safe as several
producers can obtain value at once).  Process the value and return the
result.

Once returned, it can be consumed by :py:class:`Consumer` instances -- and
results can be stored in some kind of (thread-safe) result (multiple
consumers at once can store the value at once).

:py:class:`ProducerConsumer` engine manages necessary synchronization among
:py:class:`ProducerThread` and :py:class:`ConsumerThread` threads and
provides produced objects from :py:meth:`Producer.produce` to
:py:meth:`Consumer.consume`.

Caller should ususually:

#. override :py:meth:`Producer.produce`

#. override :py:meth:`Consumer.consume`

#. define some kind of thread-safe generator if required for
   :py:class:`Producer` instances to obtain initial objects

#. define some kind of thread-safe result if required for
   :py:class:`Consumer` instances to store results

You can look in :py:class:`summer.tests.pctest.ProducerConsumerTest` for
inspiration.

Please look at :py:mod:`summer.pcg` module as a specific implementation of
producer--consumer that uses iterable as input, several producers are used
to iterate over it and produce values consumed by several consumers.

Thread count is determind based on target HW (number of cores available +
1).  You can try to experiment with this value.  For I/O heavy tasks you
can get usually better perfomance by increasing number of threads (as a
rule of thumb try twice the number of cores).

"""

import logging
import os
import threading

from .ex import AbstractMethodException
from .utils import ThreadSafeCounter

logger = logging.getLogger(__name__)


class Producer(object):

    """Producer object produces whatever is needed.  Override
    :py:meth:`produce` method.

    """

    END_OF_PRODUCTION = object()

    def produce(self) -> object:
        """Return :py:data:`Producer.END_OF_PRODUCTION` object to indicate end of
        production.

        """
        raise AbstractMethodException()


class Consumer(object):

    """Consumer object consumes whatever is produces by :py:class:`Producer`.
    Override :py:meth:`consume` method.

    """

    END_OF_CONSUMPTION = object()

    def consume(self, produced_object: object):
        raise AbstractMethodException()


class ProducerConsumer(object):

    """:py:class:`ProducerConsumer` handles necessary synchronization among
    producer and consumer threads.

    """

    DEFAULT_THREAD_COUNT = os.cpu_count() + 1

    def __init__(self,
                 producer: Producer,
                 consumer: Consumer,
                 producer_thread_count=DEFAULT_THREAD_COUNT,
                 consumer_thread_count=DEFAULT_THREAD_COUNT):
        """Creates :py:class:`ProducerConsumer` instance.

        Args:

            producer (Producer): producer instance supplied by caller

            consumer (Consumer): consumer instance supplied by caller

            producer_thread_count (int): number of producer threads

            consumer_thread_count (int): number of consumer threads

        """
        self.producer = producer
        self.consumer = consumer
        self.producer_thread_count = producer_thread_count
        self.consumer_thread_count = consumer_thread_count
        self.producer_threads = []
        self.consumer_threads = []
        # NOTE martin.slouf -- shared buffer -- producers put items, consumers
        # pop items
        self.dataflow = []
        self.dataflow_condition = threading.Condition()
        self.produced_count = ThreadSafeCounter()
        self.consumed_count = ThreadSafeCounter()
        self.producer_thread_finished_count = ThreadSafeCounter()

    def run(self):
        """Start the producer--consumer engine.  Starts the threads and waits for
        all of them to complete.

        """
        self.producer_threads = self._start_producer_threads()
        logger.debug("producer threads started")
        self.consumer_threads = self._start_consumer_threads()
        logger.debug("consumer threads started")
        for thread in self.producer_threads + self.consumer_threads:
            thread.join()
        logger.debug("producer-consumer threads joined")

    def object_produced(self, produced_object: object):
        """Called by :py:class:`ProducerThread` once the object is produced."""
        if produced_object != Producer.END_OF_PRODUCTION:
            self.produced_count.inc()
            logger.debug("produced object %s (%s)", produced_object, self)
        else:
            self.producer_thread_finished_count.inc()
        cond = self.dataflow_condition
        with cond:
            self.dataflow.append(produced_object)
            cond.notify_all()

    def object_consumed(self) -> object:
        """Called by :py:class`ConsumerThread` when the object is being consumed."""
        tmp = Producer.END_OF_PRODUCTION
        cond = self.dataflow_condition
        with cond:
            while self.__should_wait_for_producers():
                cond.wait()
            if self.dataflow:
                tmp = self.dataflow.pop(0)
            # NOTE martin.slouf -- wake up any waiting threads, if any (so
            # they won't wait indefinitely)
            cond.notify_all()
        if tmp == Producer.END_OF_PRODUCTION:
            if self.__should_end_consumption():
                tmp = Consumer.END_OF_CONSUMPTION
        else:
            self.consumed_count.inc()
            logger.debug("consumed object %s (%s)", tmp, self)
        return tmp

    def __should_wait_for_producers(self):
        cond = self.dataflow_condition
        with cond:
            return self.producer_thread_finished_count.get() < self.producer_thread_count and not self.dataflow

    def __should_end_consumption(self):
        cond = self.dataflow_condition
        with cond:
            return self.producer_thread_finished_count.get() == self.producer_thread_count and not self.dataflow

    def _start_producer_threads(self):
        threads = []
        for i in range(0, self.producer_thread_count):
            thread = ProducerThread(self, self.producer)
            thread.start()
            threads.append(thread)
        return threads

    def _start_consumer_threads(self):
        threads = []
        for i in range(0, self.consumer_thread_count):
            thread = ConsumerThread(self, self.consumer)
            thread.start()
            threads.append(thread)
        return threads

    def __str__(self):
        cond = self.dataflow_condition
        with cond:
            size = len(self.dataflow)
        tmp = "%s [producer/consumer count: %d (finished: %d) / %d, dataflow size: %d, produced/consumed count: %d / %d]" % \
              (self.__class__.__name__,
               len(self.producer_threads),
               self.producer_thread_finished_count.get(),
               len(self.consumer_threads),
               size,
               self.produced_count.get(),
               self.consumed_count.get())
        return tmp


class ProducerThread(threading.Thread):

    """Thread executing producer objects."""

    def __init__(self, producer_consumer: ProducerConsumer, producer: Producer):
        threading.Thread.__init__(self, name="producer")
        self.producer_consumer = producer_consumer
        self.producer = producer

    def run(self):
        obj = self.producer.produce()
        while obj != Producer.END_OF_PRODUCTION:
            self.producer_consumer.object_produced(obj)
            obj = self.producer.produce()
        self.producer_consumer.object_produced(Producer.END_OF_PRODUCTION)


class ConsumerThread(threading.Thread):

    """Thread executing consumer objects."""

    def __init__(self, producer_consumer: ProducerConsumer, consumer: Consumer):
        threading.Thread.__init__(self, name="consumer")
        self.producer_consumer = producer_consumer
        self.consumer = consumer

    def run(self):
        obj = self.producer_consumer.object_consumed()
        while obj != Consumer.END_OF_CONSUMPTION:
            if obj != Producer.END_OF_PRODUCTION:
                self.consumer.consume(obj)
            obj = self.producer_consumer.object_consumed()
