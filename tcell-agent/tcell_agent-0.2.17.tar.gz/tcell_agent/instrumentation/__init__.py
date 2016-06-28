# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals
from __future__ import print_function

import traceback

from .manager import InstrumentationManager

_test_mode = False

def run_instrumentations():
    """Call the instrumentation functions, only works if they exist"""
    if (InstrumentationManager.initial_instrumentation_run == False):
        InstrumentationManager.initial_instrumentation_run = True
        from tcell_agent.instrumentation import gunicorn_tcell
        from tcell_agent.instrumentation import django
        from tcell_agent.instrumentation import flask

def safe_wrap_function(description, func, *args, **kwargs):
  if (_test_mode):
    print("[tcell] >" + description + "<")
    return func(*args, **kwargs)
  try:
    return func(*args, **kwargs)
  except Exception as e:
    handle_exception(description, e)

def safe_wrap_function_no_log(description, func, *args, **kwargs):
  if (_test_mode):
    print("[tcell] >" + description + "<")
    return func(*args, **kwargs)
  try:
    return func(*args, **kwargs)
  except Exception as e:
    pass

def handle_exception(msg, e, logger=None):
  if logger:
    logger.error(e)
  else:
    print(msg)
    traceback.print_exc()

class BaseWrapper(object):
    def __init__(self, instance):
        self._instance = instance

    def __getattr__(self, attr):
        #print("Calling __getattr__: "+attr)
        if hasattr(self._instance, attr):
            def wrapper(*args, **kw):
                #print('called with %r and %r' % (args, kw))
                return getattr(self._instance, attr)(*args, **kw)
            return wrapper
        raise AttributeError(attr)