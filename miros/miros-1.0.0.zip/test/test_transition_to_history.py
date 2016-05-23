from miros.hsmfactory import *
from miros.hsmbase import Hsm
import pprint
import sys
import re
import inspect
import pytest
from miros.spy_trace_format import t, s


@pytest.fixture
def toaster_chart():
  def heater_on(heating):
    pass
  def heater_off(heating):
    pass
  def lamp_on(door_open):
    pass
  def lamp_off(door_open):
    pass

  def break_here(door_closed):
    pass

  chart = HsmFactory(
            name="transition_to_history_pattern",
            trace_formatter=t,
            spy_formatter=s)

  chart.create(state = 'door_closed'
      ).catch(event = "OFF",
              goto   = "off"
      ).catch(event = "TOAST",
              goto   = "toasting"
      ).catch(event = "BAKE",
              goto   = "baking"
      ).catch(event = "OPEN",
              goto   = "door_open")

  chart.create(state  = 'door_open'
      ).catch(event  = "entry",
              handler = lamp_on
      ).catch(event  = "exit",
              handler = lamp_off
      ).catch(event  = "CLOSE",
              goto    = 'door_closed.history')

  chart.create(state  = 'heating'
      ).catch(event  = 'entry',
              handler = heater_on
      ).catch(event  = 'exit',
              handler = heater_off)

  chart.create(state  = 'off')
  chart.create(state  = 'toasting')
  chart.create(state  = 'baking')

  chart.nest(state='door_closed', parent=None, history=True
      ).nest(state='door_open', parent=None
      ).nest(state='heating', parent='door_closed'
      ).nest(state='baking', parent='heating'
      ).nest(state='toasting', parent='heating'
      ).nest(state='off', parent='door_closed')

  chart.live_spy(True)
  chart.live_trace(False)
  return chart

def test_basic_chart(toaster_chart):
  chart = toaster_chart
  chart.trigger_start("door_closed")
  chart.trigger_event("OFF")
  chart.trigger_event("OPEN")
  chart.trigger_event("CLOSE")
  chart.trigger_event("BAKE")
  chart.trigger_event("OPEN")
  chart.trigger_event("CLOSE")
  chart.trigger_event("OFF")
  chart.trigger_event("OPEN")
  chart.trigger_event("CLOSE")
  pass

