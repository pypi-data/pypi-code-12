from miros.hsmfactory import *
from miros.hsmbase import Hsm
import pprint
import sys
import re
import inspect
import pytest
expected_spy_trace = [ "df(top-entry-{'y': 0, 'x': 0, 'z': 0, 'tik': 6})",
                       "df(top-init-{'y': 0, 'x': 0, 'z': 0, 'tik': 6})",
                       "df(d2-entry-{'y': 0, 'x': 0, 'z': 0, 'tik': 6})",
                       "df(d2-init-{'y': 0, 'x': 0, 'z': 0, 'tik': 6})",
                       "df(d21-entry-{'y': 0, 'x': 0, 'z': 0, 'tik': 6})",
                       "df(d211-entry-{'y': 0, 'x': 0, 'z': 0, 'tik': 6})",
                       "df(run-a-{'y': 0, 'x': 0, 'z': 0, 'tik': 6})",
                       "df(d211-exit-{'y': 0, 'x': 0, 'z': 0, 'tik': 6})",
                       "df(d21-exit-{'y': 0, 'x': 0, 'z': 0, 'tik': 6})",
                       "df(d21-entry-{'y': 0, 'x': 0, 'z': 0, 'tik': 6})",
                       "df(d21-init-{'y': 0, 'x': 0, 'z': 0, 'tik': 6})",
                       "df(d211-entry-{'y': 0, 'x': 0, 'z': 0, 'tik': 6})",
                       'df(run-b)',
                       'df(d211-exit)',
                       'df(d211-entry)',
                       'df(run-c)',
                       'df(d211-exit)',
                       'df(d21-exit)',
                       'df(d2-exit)',
                       'df(d1-entry)',
                       'df(d1-init)',
                       'df(d11-entry)',
                       'df(run-d)',
                       'df(d11-exit)',
                       'df(d1-init)',
                       'df(d11-entry)',
                       'df(run-e)',
                       'df(d11-exit)',
                       'df(d1-exit)',
                       'df(d1-entry)',
                       'df(d11-entry)',
                       'df(run-f)',
                       'df(d11-exit)',
                       'df(d1-exit)',
                       'df(d2-entry)',
                       'df(d21-entry)',
                       'df(d211-entry)',
                       'df(run-g)',
                       'df(d211-exit)',
                       'df(d21-exit)',
                       'df(d2-exit)',
                       'df(d1-entry)',
                       'df(d1-init)',
                       'df(d11-entry)',
                       'df(run-h)',
                       'df(d11-exit)',
                       'df(d1-exit)',
                       'df(top-init)',
                       'df(d2-entry)',
                       'df(d2-init)',
                       'df(d21-entry)',
                       'df(d211-entry)',
                       'df(run-g)',
                       'df(d211-exit)',
                       'df(d21-exit)',
                       'df(d2-exit)',
                       'df(d1-entry)',
                       'df(d1-init)',
                       'df(d11-entry)',
                       "df(run-f-{'y': 0, 'x': 0, 'z': 0, 'tik': 5})",
                       "df(d11-exit-{'y': 0, 'x': 0, 'z': 0, 'tik': 5})",
                       "df(d1-exit-{'y': 0, 'x': 0, 'z': 0, 'tik': 5})",
                       "df(d2-entry-{'y': 0, 'x': 0, 'z': 0, 'tik': 5})",
                       "df(d21-entry-{'y': 0, 'x': 0, 'z': 0, 'tik': 5})",
                       "df(d211-entry-{'y': 0, 'x': 0, 'z': 0, 'tik': 5})",
                       'df(run-e)',
                       'df(d211-exit)',
                       'df(d21-exit)',
                       'df(d2-exit)',
                       'df(d1-entry)',
                       'df(d11-entry)',
                       'df(run-d)',
                       'df(d11-exit)',
                       'df(d1-init)',
                       'df(d11-entry)',
                       'df(run-c)',
                       'df(d11-exit)',
                       'df(d1-exit)',
                       'df(d2-entry)',
                       'df(d2-init)',
                       'df(d21-entry)',
                       'df(d211-entry)',
                       'df(run-b)',
                       'df(d211-exit)',
                       'df(d211-entry)',
                       'df(run-a)',
                       'df(d211-exit)',
                       'df(d21-exit)',
                       'df(d21-entry)',
                       'df(d21-init)',
                       'df(d211-entry)']

expected_trace_trace =[ "top->d211(entry:{'y': 0, 'x': 0, 'z': 0, 'tik': 6})",
                        "d211->d211(a:{'y': 0, 'x': 0, 'z': 0, 'tik': 6})",
                        'd211->d211(b)',
                        'd211->d11(c)', # here
                        'd11->d11(d)',
                        'd11->d11(e)',
                        'd11->d211(f)',
                        'd211->d11(g)',
                        'd11->d211(h)',
                        'd211->d11(g)',
                        "d11->d211(f:{'y': 0, 'x': 0, 'z': 0, 'tik': 5})",
                        'd211->d11(e)',
                        'd11->d11(d)',
                        'd11->d211(c)',
                        'd211->d211(b)',
                        'd211->d211(a)'
                      ]
ppp = pprint.PrettyPrinter(indent=2)
def pp(thing):
  ppp.pprint(thing)

def A_init(chart,kwargs):
  if 'bob' in kwargs:
    print kwargs['bob']
  if 'mary' in kwargs:
    print kwargs['mary']
  return 0

def A_b(chart, kwargs):
  pass

def A_c(chart, kwargs):
  pass

def A_entry(chart,state):
  pass

def A_exit(chart,state):
  pass

def A_z(chart,state):
  pass

def setup_default_chart():
  chart = HsmFactory(name="under_test")
  assert(chart.name == "under_test" )
  # State created #
  chart.create(state = "A"
          # behavior described below #
          ).catch(event   = 'b',    # Catch the 'b' event
                  handler  = A_b,    # Then run this function
                  goto    = 'C',    # Trans to this state now
                  blocking = True    # Then stop (default)
          ).catch(event   = 'c',    # Catch the 'c' event
                  handler  = A_c     # Then run this function
          ).catch(event   = 'a',    # Catch the 'a' event
                  blocking = True    # And block further gotoitions
          ).catch(event   = 'd',    # Catch the 'd' event
                  blocking = True    # And block further gotoitions
          ).catch(event   = 'z',    # Catch the 'z' event
                  handler  = A_z,    # Then run this function
                  blocking = False   # Now lets 'z' flow out to a super state
          )
  pass


def test_create_chaining():
  setup_default_chart()
  chart = HsmFactory(name="under_test")
  assert(chart.name == "under_test" )
  # State created #
  chart.create(state = "A"
          # behavior described below #
          ).catch(event   = 'b',    # Catch the 'b' event
                  handler  = A_b,    # Then run this function
                  goto    = 'C',    # Trans to this state now
                  blocking = True    # Then stop (default)
          ).catch(event   = 'c',    # Catch the 'c' event
                  handler  = A_c     # Then run this function
          ).catch(event   = 'a',    # Catch the 'a' event
                  blocking = True    # And block further gotoitions
          ).catch(event   = 'd',    # Catch the 'd' event
                  blocking = True    # And block further gotoitions
          ).catch(event   = 'z',    # Catch the 'z' event
                  handler  = A_z,    # Then run this function
                  blocking = False   # Now lets 'z' flow out to a super state
          )
  #assert(chart.state("A").events["entry"].handler == chart.state("A").default_entry_handler )
  # assert(chart.state("A").events["exit"].handler == chart.state("A").default_exit_handler )
  handler_1 = chart.state("A").events["exit"].handler
  handler_2 = chart.state("A").default_exit_handler
  assert(handler_1.__name__ == handler_2.__name__)

  handler_1 = chart.state("A").events["entry"].handler
  handler_2 = chart.state("A").default_entry_handler
  assert(handler_1.__name__ == handler_2.__name__)

  #handler_1 = chart.state("A").events["init"].handler
  handler_2 = chart.state("A").default_init_handler
  #assert(handler_1.__name__ == handler_2.__name__)
  # test_create_chaining

def test_create_state_access():
  setup_default_chart()
  chart = HsmFactory(name="under_test")
  chart.create(state = "A")
  assert(chart.has_state("A") == True)
  assert(isinstance(chart.state("A"), State) == True )
  assert(chart.state("A").has_event("entry") == True )
  #assert(chart.state("A").has_event("init") == True )
  assert(chart.state("A").has_event("exit") == True )
  #assert(chart.state("A").has_event("b") == True )

# we salt away the event, then call the calling function with the 'reflect'
# event, get it's name, then put the original event back once we have enough
# information to r_and_t on our state.

def r_and_t(chart):
  """ report and tick """
  event  = chart.current['event']
  name    = chart.current['state']
  payload = chart.current['payload']
  if payload == None:
    s = "testing(%s-%s);" % (name, event)
  else:
    s = "testing(%s-%s-%s);" %(name, event, payload)
    payload['tik'] += 1
  print s
  chart.current['payload'] = None

@pytest.fixture
def vanilla_chart():
  chart = HsmFactory(name="under_test")
  chart.create(state = "top"
          # behavior described below #
          ).catch(event    = "entry", #
                  handler   = r_and_t,  #
          ).catch(event    = "exit",  #
                  handler   = r_and_t,  #
          ).catch(event    = "init",  #
                  handler   = r_and_t,  #
                  goto     = 'd2',    #
          ).catch(event    = 'reset', #
                  handler   = r_and_t,
                  goto     = "top",
          ).catch(event    = 'e',     #
                  handler   = r_and_t,  #
                  goto     = 'd11',   #
          ).catch(event    = 'c',     #
                  handler   = r_and_t   #
          ).catch(event    = 'a',     #
          ).catch(event    = 'd',     #
          ).catch(event    = 'z',     #
                  handler   = r_and_t,  #
          )

  chart.create(state = "d1"
          # behavior described below #
          ).catch(event    = "entry", #
                  handler   = r_and_t,  #
          ).catch(event    = "exit",  #
                  handler   = r_and_t,  #
          ).catch(event    = "init",  #
                  handler   = r_and_t,  #
                  goto     = 'd11',   #
          ).catch(event    = 'a',     #
                  handler   = r_and_t,  #
                  goto     = 'd1',    #
          ).catch(event    = 'c',     #
                  goto     = 'd2',    #
          ).catch(event    = 'a',     #
                  goto     = 'd1',    #
          ).catch(event    = 'f',     #
                  goto     = 'd211',  #
          )

  chart.create(state = "d11"
          # behavior described below #
          ).catch(event    = "entry", #
                  handler   = r_and_t,  #
          ).catch(event    = "exit",  #
                  handler   = r_and_t,  #
          ).catch(event    = 'd',     #
                  handler   = r_and_t,  #
                  goto     = 'd1',    #
          ).catch(event    = 'g',     #
                  goto     = 'd211',  #
          ).catch(event    = 'h',     #
                  goto     = 'top',   #
          )

  chart.create(state = "d2"
          # behavior described below #
          ).catch(event  = "entry", #
                  handler = r_and_t,  #
          ).catch(event  = "exit",  #
                  handler = r_and_t,  #
          ).catch(event  = "init",  #
                  handler = r_and_t,  #
                  goto   = 'd211',  #
          ).catch(event  = 'c',     #
                  handler = r_and_t,  #
                  goto   = 'd1',    #
          ).catch(event  = 'f',     #
                  handler = r_and_t,  #
                  goto   = 'd21',   #
          )

  chart.create(state = "d21"
          # behavior described below #
          ).catch(event  = "entry",
                  handler = r_and_t,  #
          ).catch(event  = "exit",  #
                  handler = r_and_t,  #
          ).catch(event  = "init",  #
                  handler = r_and_t,  #
                  goto    = 'd211',  #
          ).catch(event  = 'a',     #
                  handler = r_and_t,  #
                  goto    = 'd21',   #
          ).catch(event  = 'b',     #
                  handler = r_and_t,  #
                  goto    = 'd211',  #
          ).catch(event  = 'g',     #
                  handler = r_and_t,  #
                  goto    = 'd1',    #
          )

  chart.create(state = "d211"
          # behavior described below #
          ).catch(event  = "entry",
                  handler = r_and_t, #
                  block   = True
          ).catch(event  = "exit", #
                  handler = r_and_t, #
          ).catch(event  = 'd',    #
                  handler = r_and_t, #
                  goto    = 'd21',  #
          ).catch(event  = 'h',    #
                  handler = r_and_t, #
                  goto    = 'top'
          )

  chart.nest(state="top",
             parent=None,
      ).nest(state="d2",
             parent="top",
      ).nest(state="d21",
             parent="d2"
      ).nest(state="d211",
             parent="d21"
      ).nest(state="d1",
             parent="top"
      ).nest(state="d11",
             parent="d1")

  return chart

def test_building_a_state(vanilla_chart):
  def l_cp():
    pd = {}
    pd.setdefault('x', 0)
    pd.setdefault('y', 0)
    pd.setdefault('z', 0)
    pd.setdefault('tik', 0)
    return pd

  chart = vanilla_chart
  chart.trigger_start("top", payload=l_cp())
  chart.trigger_event("a",   payload=l_cp())
  chart.trigger_event("b")
  chart.trigger_event("c")
  chart.trigger_event("d")
  chart.trigger_event("e")
  chart.trigger_event("f")
  chart.trigger_event("g")
  chart.trigger_event("h")
  chart.trigger_event("g")
  chart.trigger_event("f", payload=l_cp())
  chart.trigger_event("e")
  chart.trigger_event("d")
  chart.trigger_event("c")
  chart.trigger_event("b")
  chart.trigger_event("a")

  assert(chart.hsm.spy() == expected_spy_trace)
  assert(chart.hsm.trace() == expected_trace_trace)
