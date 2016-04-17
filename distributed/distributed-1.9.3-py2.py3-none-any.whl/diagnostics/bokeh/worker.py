#!/usr/bin/env python

from __future__ import print_function, division, absolute_import

import json

from bokeh.plotting import curdoc, vplot
from tornado import gen

from distributed.diagnostics.status_monitor import (
        worker_table_plot, worker_table_update)
from distributed.utils import log_errors

import distributed.diagnostics
messages = distributed.diagnostics.messages  # global message store

doc = curdoc()

worker_source, worker_table = worker_table_plot()
@gen.coroutine
def worker_update():
    with log_errors():
        yield messages['workers']['condition'].wait()
        msg = messages['workers']['deque'][-1]
        worker_table_update(worker_source, msg)
doc.add_periodic_callback(worker_update, messages['workers']['interval'])


doc.add_root(task_table)
