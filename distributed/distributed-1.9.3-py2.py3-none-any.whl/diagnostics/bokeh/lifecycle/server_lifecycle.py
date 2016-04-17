#!/usr/bin/env python

from __future__ import print_function, division, absolute_import

from collections import deque
from datetime import datetime
import json
from time import time

from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.iostream import StreamClosedError
from tornado.ioloop import IOLoop

from distributed.core import read
from distributed.diagnostics.eventstream import eventstream
from distributed.diagnostics.progress_stream import progress_stream
from distributed.diagnostics.status_monitor import task_stream_append
import distributed.diagnostics
from distributed.utils import log_errors

client = AsyncHTTPClient()

messages = {}  # Globally visible store of messages
distributed.diagnostics.messages = messages  # monkey-patching


@gen.coroutine
def http_get(route):
    """ Get data from JSON route, store in messages deques """
    with log_errors():
        response = yield client.fetch('http://localhost:9786/%s.json' % route)
        msg = json.loads(response.body.decode())
        messages[route]['deque'].append(msg)
        messages[route]['times'].append(time())


@gen.coroutine
def task_events(interval, deque, times, index, rectangles, workers, last_seen):
    i = 0
    with log_errors():
        stream = yield eventstream('localhost:8786', 0.100)
        while True:
            try:
                msgs = yield read(stream)
            except StreamClosedError:
                break
            else:
                if not msgs:
                    continue

                last_seen[0] = time()
                for msg in msgs:
                    if 'compute-start' in msg:
                        deque.append(msg)
                        times.append(msg['compute-start'])
                        index.append(i)
                        i += 1
                        task_stream_append(rectangles, msg, workers)


@gen.coroutine
def progress():
    with log_errors():
        stream = yield progress_stream('localhost:8786', 0.100)
        while True:
            try:
                msg = yield read(stream)
            except StreamClosedError:
                break
            else:
                messages['progress'] = msg


def on_server_loaded(server_context):
    messages['workers'] = {'interval': 500,
                           'deque': deque(maxlen=60),
                           'times': deque(maxlen=60)}
    server_context.add_periodic_callback(lambda: http_get('workers'), 500)

    messages['tasks'] = {'interval': 100,
                         'deque': deque(maxlen=100),
                         'times': deque(maxlen=100)}
    server_context.add_periodic_callback(lambda: http_get('tasks'), 100)

    messages['task-events'] = {'interval': 200,
                               'deque': deque(maxlen=20000),
                               'times': deque(maxlen=20000),
                               'index': deque(maxlen=20000),
                               'rectangles':{name: deque(maxlen=20000) for name in
                                            'start duration key name color worker worker_thread'.split()},
                               'workers': set(),
                               'last_seen': [time()]}
    messages['progress'] = {'all': {}, 'in_memory': {},
                            'erred': {}, 'released': {}}

    IOLoop.current().add_callback(task_events, **messages['task-events'])
    IOLoop.current().add_callback(progress)
