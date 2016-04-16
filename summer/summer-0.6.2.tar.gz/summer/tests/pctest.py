# -*- coding: utf-8 -*-
# Time-stamp: < pctest.py (2016-02-07 07:53) >

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

import logging
import threading
import unittest

from summer import Producer, Consumer, ProducerConsumer

logger = logging.getLogger(__name__)


class ProducerConsumerTest(unittest.TestCase):

    def setUp(self):
        self.result = Result()
        self.generator = Generator()
        self.producer = NumberProducer(self.generator)
        self.consumer = NumberConsumer(self.result)

    def tearDown(self):
        pass

    def test_generator(self):
        counter = 0
        while self.generator.has_next():
            self.assertTrue(self.generator.has_next())
            tmp = self.generator.next()
            for i in tmp:
                self.assertEqual(i, counter)
                counter += 1

    def test_run_single_producer_single_consumer(self):
        logger.info("test_run_single_producer_single_consumer")
        producer_consumer = ProducerConsumer(
            self.producer, self.consumer, 1, 1)
        producer_consumer.run()
        self.common_asserts(producer_consumer)

    def test_run_multiple_producer_single_consumer(self):
        logger.info("test_run_multiple_producer_single_consumer")
        producer_consumer = ProducerConsumer(
            self.producer, self.consumer, 5, 1)
        producer_consumer.run()
        self.common_asserts(producer_consumer)

    def test_run_single_producer_multiple_consumer(self):
        logger.info("test_run_single_producer_multiple_consumer")
        producer_consumer = ProducerConsumer(
            self.producer, self.consumer, 1, 5)
        producer_consumer.run()
        self.common_asserts(producer_consumer)

    def test_run_multiple_producer_multiple_consumer(self):
        logger.info("test_run_multiple_producer_multiple_consumer")
        producer_consumer = ProducerConsumer(
            self.producer, self.consumer, 2, 2)
        producer_consumer.run()
        self.common_asserts(producer_consumer)

    def test_run_multiple_producer_multiple_consumer_default(self):
        logger.info("test_run_multiple_producer_multiple_consumer")
        producer_consumer = ProducerConsumer(self.producer, self.consumer)
        producer_consumer.run()
        self.common_asserts(producer_consumer)

    def common_asserts(self, producer_consumer):
        produced_count = int(Generator.MAX_VALUE / Generator.INTERVAL_SIZE)
        self.assertEqual(
            produced_count, producer_consumer.produced_count.get())
        self.assertEqual(
            produced_count, producer_consumer.consumed_count.get())
        col = sorted(self.result.list)
        for i in range(0, Generator.MAX_VALUE, 1):
            self.assertEqual(i, col[i])


class Generator(object):

    """Stateful object."""

    MAX_VALUE = 1000
    INTERVAL_SIZE = 10

    NO_PEEK_SET = object()

    def __init__(self):
        self.max_value = Generator.MAX_VALUE
        self.interval_size = Generator.INTERVAL_SIZE
        self.lock = threading.Lock()
        self.iterable = self.__create_intervals()
        # NOTE martin 2015-09-27 -- element to be returned during the next
        # next() call
        self.peek = Generator.NO_PEEK_SET
        # NOTE martin 2015-09-27 -- internal iterator / generator
        self.it = self.__next_element()

    def __create_intervals(self):
        intervals = []
        values = []
        for i in range(0, self.max_value, 1):
            if i % self.interval_size == 0:
                values = []
                intervals.append(values)
            values.append(i)
        return intervals

    def has_next(self):
        with self.lock:
            if self.peek == Generator.NO_PEEK_SET:
                try:
                    self.peek = next(self.it)
                except StopIteration:
                    self.peek = Generator.NO_PEEK_SET
            return self.peek != Generator.NO_PEEK_SET

    def next(self):
        with self.lock:
            if self.peek != Generator.NO_PEEK_SET:
                tmp = self.peek
                self.peek = Generator.NO_PEEK_SET
                return tmp
            raise StopIteration()

    def __next_element(self):
        for i in self.iterable:
            yield i


class Result(object):

    def __init__(self):
        self.lock = threading.Lock()
        self.list = []

    def append(self, obj):
        with self.lock:
            self.list.append(obj)


class NumberProducer(Producer):

    def __init__(self, generator):
        Producer.__init__(self)
        self.generator = generator

    def produce(self):
        if self.generator.has_next():
            try:
                # NOTE martin 2015-09-27 -- several threads will call has_next,
                # but only one will succeed, so ignore the potential exception
                return self.generator.next()
            except StopIteration:
                pass
        return Producer.END_OF_PRODUCTION


class NumberConsumer(Consumer):

    def __init__(self, result):
        Consumer.__init__(self)
        self.result = result

    def consume(self, produced_object):
        for i in produced_object:
            self.result.append(i)
