"""
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  This file is part of the Smart Developer Hub Project:
    http://www.smartdeveloperhub.org

  Center for Open Middleware
        http://www.centeropenmiddleware.com/
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  Copyright (C) 2015 Center for Open Middleware.
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

            http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
"""

__author__ = 'Fernando Serena'

import logging

from agora.stoa.client import get_fragment_generator

__triple_patterns = {}
__plan_patterns = {}

log = logging.getLogger('sdh.fragments.provider.collect')


def collect(tp, *args):
    """
    Decorator to attach a collector function to a triple pattern
    :param tp:
    :param args:
    :return:
    """

    def decorator(f):
        add_triple_pattern(tp, f, args)

    return decorator


def add_triple_pattern(tp, collector, args):
    """0
    Manage the relations between triple patterns and collector functions
    :param tp:
    :param collector:
    :param args:
    :return:
    """
    tp_parts = [part.strip() for part in tp.strip().split(' ')]
    tp = ' '.join(tp_parts)
    if tp not in __triple_patterns.keys():
        __triple_patterns[tp] = set([])
    if collector is not None:
        __triple_patterns[tp].add((collector, args))


def collect_fragment(event, **kwargs):
    """
    Execute a search plan for the declared graph pattern and send all obtained triples to the corresponding
    collector functions
    """

    extra_params = {'STOA': kwargs}

    prefixes, gen = get_fragment_generator(*__triple_patterns, stop_event=event, wait=True, **extra_params)
    log.info('pulling ' + str(__triple_patterns))

    for headers, quad in gen:
        t, s, p, o = quad
        t = ' '.join(t)
        collectors = __triple_patterns[t]
        for c, args in collectors:
            log.debug('Sending triple {} {} {} to {}'.format(s.n3(), p.n3(),
                                                             o.n3(), c))
            c((s, p, o))
            yield (c.func_name, (t, s, p, o))
        if event.isSet():
            break
    if event.isSet():
        raise Exception('Abort collecting fragment')

    log.debug('finished with ' + str(__triple_patterns))
