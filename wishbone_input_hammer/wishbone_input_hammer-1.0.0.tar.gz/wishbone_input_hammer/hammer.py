#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       hammer.py
#
#       Copyright 2016 Jelle Smet development@smetj.net
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 3 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#
#

from wishbone import Actor
from time import time
from random import randint
from gevent import sleep
from gevent.socket import gethostname
from gevent import spawn
from wishbone.event import Event, Metric


class Hammer(Actor):

    '''**Generates random metric events.**

    Generates random metrics events in the Wishbone internal Metric format.

    Metrics names will have following name structure:

        <prefix>.set_<batch_size>.metric_<set_size>

        hammer.set_0.metric_0 34534 1382173076


    Parameters:

        - batch(int)(0)
            |  The number of batches to produce.
            |  0 is unlimited.

        - batch_size(int)(1)
            |  The number of unique data sets in 1 batch.

        - set_size(int)(1)
            |  The number of unique metrics per set.

        - sleep(float)(1)
            |  The time to sleep in between generating batches.

        - value (int)(1)
            |  The maximum of the randomized metric value (default 1).

        - tags(set)()
            |  A list of unique tags

    Queues:

        - outbox
           |  Outgoing messges

    '''

    def __init__(self, actor_config, batch=0, batch_size=1, set_size=1, sleep=1, value=1, tags=()):
        Actor.__init__(self, actor_config)

        if batch == 0:
            self.generateNextBatchAllowed = self.__returnTrue
        else:
            self.generateNextBatchAllowed = self.__evaluateCounter

        self.pool.createQueue("outbox")
        self.hostname = gethostname()

    def preHook(self):
        spawn(self.generate)

    def generate(self):
        batch_counter = 0
        while self.loop():
            if self.generateNextBatchAllowed(batch_counter) is True:
                for metric in self.generateBatch():
                    event = Event(metric)
                    self.submit(event, self.pool.queue.outbox)
                batch_counter += 1
            else:
                self.logging.warn('Reached the batch_size of %s.  Not generating any further metrics.' % (self.kwargs.batch_size))
                break
            sleep(self.kwargs.sleep)

    def generateBatch(self):

        for set_name in xrange(self.kwargs.batch_size):
            for metric_name in xrange(self.kwargs.set_size):
                yield Metric(time(), "hammer", self.hostname, 'set_%s.metric_%s' % (set_name, metric_name), randint(0, self.kwargs.value), '', self.kwargs.tags)

    def __evaluateCounter(self, counter):
        if counter == self.batch:
            return False
        else:
            return True

    def __returnTrue(self, counter):
        return True

