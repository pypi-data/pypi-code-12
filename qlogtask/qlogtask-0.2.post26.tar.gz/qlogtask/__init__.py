#! /usr/bin/env python

from __future__ import absolute_import
import celery, json, logging, logtool, os, socket, time
from celery import signals
from ._version import get_versions
__version__ = get_versions ()['version']
__version_info__ = get_versions ()
del get_versions

LOG = logging.getLogger (__name__)

@logtool.log_call (log_rc = False)
def send_event (event):
  # pylint: disable=E0611
  celery.execute.send_task ( # pylint: disable = E1101
    "qeventlog.tasks.log",
    args = (event["timestamp"],),
    kwargs = event,
    exchange = "qeventlog",
    queue = "qeventlog")

@logtool.log_call (log_exit = False)
def get_event (event):
  return {
    "event": event,
    "hostname": socket.gethostname (),
    "pid": os.getpid (),
    "task": None, # Should be updated by every event
    "timestamp": time.time (),
  }

@logtool.log_call (log_exit = False)
@signals.before_task_publish.connect
def qetask_before_task_publish (**kwargs):
  if kwargs["sender"] == "qeventlog.tasks.log":
    return
  body = kwargs["body"]
  event = get_event ("before_task_publish")
  event.update ({
    "args": body["args"],
    "eta": body["eta"],
    "expires": body["expires"],
    "exchange": kwargs["exchange"],
    "kwargs": body["kwargs"],
    "task": body["task"],
    "retries": body["retries"],
    "task_id": body["id"],
  })
  send_event (event)

@logtool.log_call (log_exit = False)
@signals.after_task_publish.connect
def qetask_after_task_publish (**kwargs):
  if kwargs["sender"] == "qeventlog.tasks.log":
    return
  body = kwargs["body"]
  event = get_event ("after_task_publish")
  event.update ({
    "args": body["args"],
    "eta": body["eta"],
    "expires": body["expires"],
    "exchange": kwargs["exchange"],
    "kwargs": body["kwargs"],
    "task": body["task"],
    "retries": body["retries"],
    "task_id": body["id"],
    "parent_id": (celery.current_task.request.id
                  if celery.current_task else None),
  })
  send_event (event)

@logtool.log_call (log_exit = False)
@signals.task_prerun.connect
def qetask_task_prerun (**kwargs):
  if kwargs["sender"] == "qeventlog.tasks.log":
    return
  event = get_event ("task_prerun")
  event.update ({
    "args": kwargs["args"],
    "codepoint": repr (kwargs["task"]),
    "kwargs": kwargs["kwargs"],
    "task": kwargs["sender"].request.task,
    "task_id": kwargs["task_id"],
    "retries": 0,
  })
  send_event (event)

@logtool.log_call (log_exit = False)
@signals.task_postrun.connect
def qetask_task_postrun (**kwargs):
  if kwargs["sender"] == "qeventlog.tasks.log":
    return
  event = get_event ("task_postrun")
  event.update ({
    "args": kwargs["args"],
    "codepoint": repr (kwargs["task"]),
    # Duration?
    "kwargs": kwargs["kwargs"],
    "retval": (repr (kwargs["retval"])
               if isinstance (kwargs["retval"], Exception)
               else json.dumps (kwargs["retval"])),
    "state": kwargs["state"],
    "task": kwargs["sender"].request.task,
    "task_id": kwargs["task_id"],
    "retries": kwargs["task"].request.retries,
  })
  send_event (event)

@logtool.log_call (log_exit = False)
@signals.task_retry.connect
def qetask_task_retry (**kwargs):
  if kwargs["sender"] == "qeventlog.tasks.log":
    return
  event = get_event ("task_retry")
  request = kwargs["request"]
  event.update ({
    "args": request.args,
    "eta": request.eta,
    "exception": repr (kwargs["reason"]),
    "kwargs": request.kwargs,
    "expires": request.expires,
    "retries": request.retries,
    "task": request.task,
    "traceback": kwargs["einfo"].traceback,
    "task_id": request.id,
  })
  send_event (event)

@signals.task_success.connect
@logtool.log_call (log_exit = False)
def qetask_task_success (**kwargs):
  if kwargs["sender"] == "qeventlog.tasks.log":
    return
  event = get_event ("task_success")
  request = kwargs["sender"].request # task_success is weird
  event.update ({
    "args": request.args,
    "codepoint": repr (kwargs["sender"]),
    "eta": request.eta,
    "expires": request.expires,
    "kwargs": request.kwargs,
    "result": kwargs["result"],
    "retries": request.retries,
    "task": request.task,
    "task_id": request.id,
  })
  send_event (event)

@logtool.log_call (log_exit = False)
@signals.task_failure.connect
def qetask_task_failure (**kwargs):
  if kwargs["sender"] == "qeventlog.tasks.log":
    return
  event = get_event ("task_failure")
  event.update ({
    "args": kwargs["args"],
    "kwargs": kwargs["kwargs"],
    "exception": repr (kwargs["einfo"].exception),
    "task": celery.current_task.request.task if celery.current_task else None,
    "traceback": kwargs["einfo"].traceback,
    "task_id": kwargs["task_id"],
    "retries": celery.current_task.request.retries,
  })
  send_event (event)

@logtool.log_call (log_exit = False)
@signals.task_revoked.connect
def qetask_task_revoked (**kwargs):
  if kwargs["sender"] == "qeventlog.tasks.log":
    return
  event = get_event ("task_revoked")
  event.update ({
    "expired": kwargs["expired"],
    "signum": kwargs["signum"],
    "task": celery.current_task.request.task if celery.current_task else None,
    "terminated": kwargs["terminated"],
    "task_id": kwargs["task_id"],
    "retries": kwargs["body"]["retries"],
  })
  send_event (event)

@logtool.log_call
def qetask_install ():
  LOG.info ("QETask signal handlers installed.")
