import os
import sys
sys.path.insert(0, os.path.abspath("../miros/"))
from miros.hsmfactory import HsmFactory, pp
from miros.hsmbase import PostEvent
from miros.spy_trace_format import *
from miros.hsmfactory import *
from miros.hsmbase import Hsm

import sys
import re
import inspect
import pytest
import pprint
import time

ppp = pprint.PrettyPrinter(indent=2)
def pp(thing):
  ppp.pprint(thing)

TOK = "toc"
TIK = "tik"

@pytest.fixture
def reminder_chart():
  def create_TIME_OUT_event(chart):
    pass

  def pollSensor(chart):
    tik = chart.current['payload'][TIK]
    if tik % 4 is 0:
      chart.post_fifo(event="DATA_READY",payload=chart.current['payload'])

  def processData(chart):
    tik = chart.current['payload'][TIK]
    if tik % 4 is 0:
      chart.goto("idle") # referencing the hsmbase.py api to gotoition to
                              # idle

  def s( time, state, event, payload, chart=None ):
    if payload is None:
      return "%s: %s" % (event, state)
    else:
      return "%s: %s:: %s" % (event, state, payload)

  def t( time, state_n_0, state_n_1, event, payload, chart=None ):
    if payload is None:
      return "%s: %s->%s" % (event, state_n_0, state_n_1)
    else:
      return "%s: %s->%s:: %s" % (event, state_n_0, state_n_1, payload)

  chart = HsmFactory(
            name="reminder_pattern",
            trace_formatter=t,
            spy_formatter=s)

  chart.create(state  = 'polling'
      ).catch(event  = 'init',
              goto   = 'processing'
      ).catch(event  = 'entry',
              handler = create_TIME_OUT_event
      ).catch(event  = 'TIME_OUT',
              handler = pollSensor
      ).catch(event  = 'RESET_CHART',
              goto   = 'polling')

  chart.create(state = 'processing'
      ).catch(event = 'init',
              goto  = 'idle')

  chart.create(state = 'idle'
      ).catch(event = 'DATA_READY',
              goto  = 'busy' )

  chart.create(state = 'busy'
      ).catch(event = 'TIME_OUT',
              handler = processData)

  chart.nest(state='polling', parent=None
      ).nest(state='processing', parent='polling'
      ).nest(state='idle', parent='processing'
      ).nest(state='busy', parent='processing')
  chart.live_spy(False)
  chart.live_trace(False) # this will change the chart dynamics
  return chart

def test_reminder_pattern_spy(reminder_chart):
  chart = reminder_chart
  chart.post_event(times=20, period=0.3, event="TIME_OUT", tick_name=TIK)
  chart.post_event(times=4, period=1.3, event="IGNORE_ME", tick_name=TOK)
  chart.trigger_start('polling')
  time.sleep(3)
  chart.trigger_event("RESET_CHART")
  chart.trigger_event("IGNORE_ME")
  time.sleep(20*0.3)
  pp(chart.spy())
  #import pdb;pdb.set_trace()
  #assert( chart.spy() == [
  #'entry: polling',
  #'init: polling',
  #'entry: processing',
  #'init: processing',
  #'entry: idle',
  #"IGNORE_ME: ignored:: {'toc': 3}",
  #"DATA_READY: run:: {'tik': 19}",
  #"exit: idle:: {'tik': 19}",
  #"entry: busy:: {'tik': 19}",
  #"TIME_OUT: processData:: {'tik': 19}",
  #"exit: busy:: {'tik': 19}",
  #"entry: idle:: {'tik': 19}",
  #"IGNORE_ME: ignored:: {'toc': 3}",
  #"DATA_READY: run:: {'tik': 19}",
  #"exit: idle:: {'tik': 19}",
  #"entry: busy:: {'tik': 19}",
  #"IGNORE_ME: ignored:: {'toc': 3}",
  #'RESET_CHART: run',
  #'exit: busy',
  #'exit: processing',
  #'exit: polling',
  #'entry: polling',
  #'init: polling',
  #'entry: processing',
  #'init: processing',
  #'entry: idle',
  #'IGNORE_ME: ignored',
  #"DATA_READY: run:: {'tik': 19}",
  #"exit: idle:: {'tik': 19}",
  #"entry: busy:: {'tik': 19}",
  #"IGNORE_ME: ignored:: {'toc': 3}",
  #"TIME_OUT: processData:: {'tik': 19}",
  #"exit: busy:: {'tik': 19}",
  #"entry: idle:: {'tik': 19}"])

def test_reminder_pattern_trace(reminder_chart):
  chart = reminder_chart
  chart.post_event(times=20, period=0.3, event="TIME_OUT", tick_name=TIK)
  chart.post_event(times=4, period=1.3, event="IGNORE_ME", tick_name=TOK)
  chart.trigger_start('polling')
  time.sleep(3)
  chart.trigger_event("RESET_CHART")
  chart.trigger_event("IGNORE_ME")
  time.sleep(20*0.3)
  pp(chart.trace())
  #assert( chart.trace() == [
  # 'entry: polling->idle',
  # "DATA_READY: idle->busy:: {'tik': 0}",
  # "TIME_OUT: busy->idle:: {'tik': 4}",
  # "DATA_READY: idle->busy:: {'tik': 8}",
  # 'RESET_CHART: busy->idle',
  # "DATA_READY: idle->busy:: {'tik': 12}",
  # "TIME_OUT: busy->idle:: {'tik': 16}"
  #])
