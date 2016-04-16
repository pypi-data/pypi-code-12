# -*- coding: utf-8 -*-
# Time-stamp: < pcg.py (2016-02-14 14:53) >

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

"""``pcg`` module is more specific producer--consumer implementation based
on common use case: If you need to iterate in parallel over a collection of
input values and invoke an operation for each item.

Typicall usage::

    class MyConsumer(Consumer):

    def __init__(self, progress: Progress):
        self.progress = progress

    def consume(self, produced_object):
        # do whatever is required to do
        self...
        # indicate progress -- for example to some gui listener (progressbar, ...)
        self.progress.next_step()

    if __name__ == "__main__":
        iterable = list(...)
        consumer = EditionConsumer(self, progress)
        pcg = ProducerConsumerWithGenerator(iterable, ProducerWithGenerator(), consumer)
        pcg.run()

Producer is replaced with :py:class:`ProducerWithGenerator` which may be
left as is usually -- it automatically iterates over provided iterable
returning one value at a time.  You can override
:py:meth:`ProducerWithGenerator.produce_from_slice` method which takes
single argument -- the current iterator value.

You can also leverage :py:func:`summer.utils.chunks` function to split
large collection into smaller ones and produce chunks of data to decrease
race conditions in iteration over single iterator --
:py:class:`summer.pc.Consumer` class consumes the whole chunks, not single
items, which may improve perfomance.

"""

import collections
import logging
import threading

from .ex import UnsupportedMethodException
from .pc import (
    Producer,
    Consumer,
    ProducerThread,
    ProducerConsumer,
)

logger = logging.getLogger(__name__)


class ThreadSafeIterator(collections.Iterator):

    """Implements thread safe iteration over an iterable."""

    def __init__(self, iterable: collections.Iterable):
        self.iterable = iterable
        self.lock = threading.Lock()
        self.iterator = iter(self.iterable)

    def __next__(self):
        with self.lock:
            return next(self.iterator)


class ProducerWithGenerator(Producer):

    """Specific version of :py:class:`summer.pc.Producer` for
    :py:class:`ProducerConsumerWithGenerator` engine.

    """

    def produce(self):
        msg = "use produce(generator_slice) instead of produce()"
        raise UnsupportedMethodException(msg)

    def produce_from_slice(self, generator_slice: object) -> object:
        """Take a slice and produce whatever needs to be produced.  Default
        implementation just returns the slice (which is handy in case we
        just want to iterate over provided iterable).

        Args:

            generator_slice: single item from iteration, whatever it may be

        Returns:

            object: whatever is desired, default implementation just
                    returns the passed item, which is reasonable if you
                    want just to iterate in parallel over iterable.

        """
        return generator_slice


class ProducerConsumerWithGenerator(ProducerConsumer):

    """Specific implementation of :py:class:`summer.pc.ProducerConsumer` that
    adds thread-safe iteration over provided *iterable* object passing
    single values to :py:class:`ProducerWithGenerator` instances one at a
    time.

    """

    def __init__(self,
                 iterable: collections.Iterable,
                 producer: ProducerWithGenerator,
                 consumer: Consumer,
                 producer_thread_count=ProducerConsumer.DEFAULT_THREAD_COUNT,
                 consumer_thread_count=ProducerConsumer.DEFAULT_THREAD_COUNT):
        """Creates :py:class:`ProducerConsumerWithGenerator` instance.

        Args:

            iterable (collections.Iterable): iterable over input values

            producer (Producer): producer instance supplied by caller

            consumer (Consumer): consumer instance supplied by caller

            producer_thread_count (int): number of producer threads

            consumer_thread_count (int): number of consumer threads

        """
        ProducerConsumer.__init__(self,
                                  producer,
                                  consumer,
                                  producer_thread_count,
                                  consumer_thread_count)
        self.iterable = iterable

    def _start_producer_threads(self):
        generator = ThreadSafeIterator(self.iterable)
        threads = []
        for i in range(0, self.producer_thread_count):
            thread = ProducerThreadWithGenerator(self,
                                                 self.producer,
                                                 generator)
            thread.start()
            threads.append(thread)
        return threads


class ProducerThreadWithGenerator(ProducerThread):

    """Thread executing producer instances
    (ie. :py:class:`ProducerWithGenerator`).

    """

    def __init__(self,
                 producer_consumer: ProducerConsumerWithGenerator,
                 producer: ProducerWithGenerator,
                 generator: ThreadSafeIterator):
        ProducerThread.__init__(self, producer_consumer, producer)
        self.generator = generator

    def run(self):
        for i in self.generator:
            obj = self.producer.produce_from_slice(i)
            self.producer_consumer.object_produced(obj)
        self.producer_consumer.object_produced(Producer.END_OF_PRODUCTION)
