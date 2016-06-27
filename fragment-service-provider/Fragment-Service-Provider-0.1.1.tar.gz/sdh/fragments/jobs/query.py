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

import logging

from agora.stoa.client import get_query_generator

__author__ = 'Fernando Serena'

__graph_patterns = {}

log = logging.getLogger('sdh.fragments.provider.query')


def query(gp, *args):
    """
    Decorator to attach a query function to both query id and triple pattern
    :param qid:
    :param tp:
    :param args:
    :return:
    """

    def decorator(f):
        add_query_pattern(gp, f, args)

    return decorator


def add_query_pattern(gp, listener, args):
    """
    Manage the relations between triple patterns and query functions
    :param gp:
    :param listener:
    :param args:
    :return:
    """
    gp = str(gp)
    if gp not in __graph_patterns.keys():
        __graph_patterns[gp] = set([])
    if listener is not None:
        __graph_patterns[gp].add((listener, args))


def execute_queries(event, **kwargs):
    """
    Execute a query for the declared graph pattern and sends all obtained results to the corresponding listener
    functions
    """

    for gp in __graph_patterns:
        prefixes, gen = get_query_generator(*eval(gp), stop_event=event, wait=True, **kwargs)
        log.info('querying ' + str(__graph_patterns))

        if gen is not None:
            for headers, res in gen:
                print headers, res
                listeners = __graph_patterns[gp]
                for c, args in listeners:
                    log.debug('Sending result {} to {}'.format(res, c))
                    c(res)
                    yield (c.func_name, res)
                if event.isSet():
                    break
        if event.isSet():
            raise Exception('Abort getting query results')

        log.debug('finished with ' + str(__graph_patterns))
