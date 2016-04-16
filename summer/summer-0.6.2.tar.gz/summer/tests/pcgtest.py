# -*- coding: utf-8 -*-
# Time-stamp: < pcgtest.py (2016-01-20 09:04) >

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
import unittest

from summer import ProducerWithGenerator, ProducerConsumerWithGenerator

from summer.tests.pctest import (
    Generator,
    Result,
    NumberConsumer
)

logger = logging.getLogger(__name__)


class ProducerConsumerWithGeneratorTest(unittest.TestCase):

    def setUp(self):
        self.result = Result()
        self.consumer = NumberConsumer(self.result)

    def tearDown(self):
        pass

    def test_run_multiple_producer_multiple_consumer_default(self):
        generator = Generator()
        iterable = generator.iterable
        producer_consumer = ProducerConsumerWithGenerator(
            iterable, ProducerWithGenerator(), self.consumer)
        producer_consumer.run()
        self.common_asserts(producer_consumer)

    def common_asserts(self, producer_consumer):
        produced_count = Generator.MAX_VALUE / Generator.INTERVAL_SIZE
        self.assertEqual(
            produced_count, producer_consumer.produced_count.get())
        self.assertEqual(
            produced_count, producer_consumer.consumed_count.get())
        col = sorted(self.result.list)
        for i in range(0, Generator.MAX_VALUE, 1):
            self.assertEqual(i, col[i])
