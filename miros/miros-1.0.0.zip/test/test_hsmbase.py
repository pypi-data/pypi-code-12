import os
import sys
sys.path.insert(0, os.path.abspath("../miros/"))
import pytest
from miros.hsmbase import Hsm
import sys
import inspect
import re
import pprint
import pytest

def expected_spy():
  return ['spy(d-entry)',
          'spy(d-init)',
          'spy(d2-entry)',
          'spy(d2-init)',
          'spy(d21-entry)',
          'spy(d211-entry)',
          'spy(d21-a)',
          'spy(d211-exit)',
          'spy(d21-exit)',
          'spy(d21-entry)',
          'spy(d21-init)',
          'spy(d211-entry)',
          'spy(d21-b)',
          'spy(d211-exit)',
          'spy(d211-entry)',
          'spy(d2-c)',
          'spy(d211-exit)',
          'spy(d21-exit)',
          'spy(d2-exit)',
          'spy(d1-entry)',
          'spy(d1-init)',
          'spy(d11-entry)',
          'spy(d11-d)',
          'spy(d11-exit)',
          'spy(d1-init)',
          'spy(d11-entry)',
          'spy(d-e)',
          'spy(d11-exit)',
          'spy(d1-exit)',
          'spy(d1-entry)',
          'spy(d11-entry)',
          'spy(d1-f)',
          'spy(d11-exit)',
          'spy(d1-exit)',
          'spy(d2-entry)',
          'spy(d21-entry)',
          'spy(d211-entry)',
          'spy(d21-g)',
          'spy(d211-exit)',
          'spy(d21-exit)',
          'spy(d2-exit)',
          'spy(d1-entry)',
          'spy(d1-init)',
          'spy(d11-entry)',
          'spy(d11-h)',
          'spy(d11-exit)',
          'spy(d1-exit)',
          'spy(d-init)',
          'spy(d2-entry)',
          'spy(d2-init)',
          'spy(d21-entry)',
          'spy(d211-entry)',
          'spy(d21-g)',
          'spy(d211-exit)',
          'spy(d21-exit)',
          'spy(d2-exit)',
          'spy(d1-entry)',
          'spy(d1-init)',
          'spy(d11-entry)',
          'spy(d1-f)',
          'spy(d11-exit)',
          'spy(d1-exit)',
          'spy(d2-entry)',
          'spy(d21-entry)',
          'spy(d211-entry)',
          'spy(d-e)',
          'spy(d211-exit)',
          'spy(d21-exit)',
          'spy(d2-exit)',
          'spy(d1-entry)',
          'spy(d11-entry)',
          'spy(d11-d)',
          'spy(d11-exit)',
          'spy(d1-init)',
          'spy(d11-entry)',
          'spy(d1-c)',
          'spy(d11-exit)',
          'spy(d1-exit)',
          'spy(d2-entry)',
          'spy(d2-init)',
          'spy(d21-entry)',
          'spy(d211-entry)',
          'spy(d21-b)',
          'spy(d211-exit)',
          'spy(d211-entry)',
          'spy(d21-a)',
          'spy(d211-exit)',
          'spy(d21-exit)',
          'spy(d21-entry)',
          'spy(d21-init)',
          'spy(d211-entry)']
global hsm_reporting_log

hsm_reporting_log = []
pp = pprint.PrettyPrinter(indent=2)

def report( self, state, event ):
  s = "testing(%s-%s);" % (state, event)
  hsm_reporting_log.append(s)
  if self.live_chart_reflection:
    print s

def d(self):

  if self.tEvt['event'] == "init":
    # display event
    report(self, sys._getframe().f_code.co_name, self.tEvt['event'])
   # gotoition to state d2.
    self.state_start(d2)
    # returning a 0 indicates event was handled
    return 0

  elif self.tEvt['event'] == "entry":
    # display event % do nothing
    # else except indicate it was handled
    report(self, sys._getframe().f_code.co_name, self.tEvt['event'])
    return 0

  elif self.tEvt['event'] == "exit":
    report(self, sys._getframe().f_code.co_name, self.tEvt['event'])
    return 0

  elif self.tEvt['event'] == "e":
    report(self, sys._getframe().f_code.co_name, self.tEvt['event'])
    self.goto(d11)
    return 0

  elif self.tEvt['event'] == "reset":
    report(self, sys._getframe().f_code.co_name, self.tEvt['event'])
    self.goto(d)
    return 0

  return self.tEvt['event']

# ====================================

def d1(self):

  if self.tEvt['event'] == "init":
    report(self, sys._getframe().f_code.co_name, self.tEvt['event'])
    self.state_start(d11)
    return 0

  elif self.tEvt['event'] == "entry":
    report(self, sys._getframe().f_code.co_name, self.tEvt['event'])
    return 0

  elif self.tEvt['event'] == "exit":
    report(self, sys._getframe().f_code.co_name, self.tEvt['event'])
    return 0

  elif self.tEvt['event'] == "a":
    report(self, sys._getframe().f_code.co_name, self.tEvt['event'])
    self.goto(d1)
    return 0

  elif self.tEvt['event'] == "b":
    report(self, sys._getframe().f_code.co_name, self.tEvt['event'])
    self.goto(d11)
    return 0

  elif self.tEvt['event'] == "c":
    report(self, sys._getframe().f_code.co_name, self.tEvt['event'])
    self.goto(d2)
    return 0

  elif self.tEvt['event'] == "f":
    report(self, sys._getframe().f_code.co_name, self.tEvt['event'])
    self.goto("d211")
    return 0

  return self.tEvt['event']

#
# ====================================

def d11(self):
  if self.tEvt['event'] == "entry":
    report(self, sys._getframe().f_code.co_name, self.tEvt['event'])
    return 0
  elif self.tEvt['event'] == "exit":
    report(self, sys._getframe().f_code.co_name, self.tEvt['event'])
    return 0
  elif self.tEvt['event'] == "d":
    report(self, sys._getframe().f_code.co_name, self.tEvt['event'])
    self.goto(d1)
    return 0
  elif self.tEvt['event'] == "g":
    report(self, sys._getframe().f_code.co_name, self.tEvt['event'])
    self.goto(d211)
    return 0
  elif self.tEvt['event'] == "h":
    report(self, sys._getframe().f_code.co_name, self.tEvt['event'])
    self.goto(d)
    return 0
  return self.tEvt['event']

# ====================================

def d2(self):
  if self.tEvt['event'] == "init":
    report(self, sys._getframe().f_code.co_name, self.tEvt['event'])
    self.state_start(d211)
    return 0
  elif self.tEvt['event'] == "entry":
    report(self, sys._getframe().f_code.co_name, self.tEvt['event'])
    return 0
  elif self.tEvt['event'] == "exit":
    report(self, sys._getframe().f_code.co_name, self.tEvt['event'])
    return 0
  elif self.tEvt['event'] == "c":
    report(self, sys._getframe().f_code.co_name, self.tEvt['event'])
    self.goto(d1)
    return 0
  elif self.tEvt['event'] == "f":
    report(self, sys._getframe().f_code.co_name, self.tEvt['event'])
    self.goto(d11)
    return 0
  return self.tEvt['event']

#
# ====================================

def d21(self):
  if self.tEvt['event'] == "init":
    report(self, sys._getframe().f_code.co_name, self.tEvt['event'])
    self.state_start(d211)
    return 0
  elif self.tEvt['event'] == "entry":
    report(self, sys._getframe().f_code.co_name, self.tEvt['event'])
    return 0
  elif self.tEvt['event'] == "exit":
    report(self, sys._getframe().f_code.co_name, self.tEvt['event'])
    return 0
  elif self.tEvt['event'] == "a":
    #import pdb; pdb.set_trace()
    report(self, sys._getframe().f_code.co_name, self.tEvt['event'])
    self.goto(d21)
    return 0
  elif self.tEvt['event'] == "b":
    report(self, sys._getframe().f_code.co_name, self.tEvt['event'])
    self.goto(d211)
    return 0
  elif self.tEvt['event'] == "g":
    report(self, sys._getframe().f_code.co_name, self.tEvt['event'])
    self.goto(d1)
    return 0
  return self.tEvt['event']

# ====================================

def d211(self):
  if self.tEvt['event'] == "entry":
    #import pdb; pdb.set_trace()
    report(self, sys._getframe().f_code.co_name, self.tEvt['event'])
    return 0
  elif self.tEvt['event'] == "exit":
    report(self, sys._getframe().f_code.co_name, self.tEvt['event'])
    return 0
  elif self.tEvt['event'] == "d":
    report(self, sys._getframe().f_code.co_name, self.tEvt['event'])
    self.rNext = {}
    return 0
  elif self.tEvt['event'] == "h":
    report(self, sys._getframe().f_code.co_name, self.tEvt['event'])
    self.goto("top")
    return 0
  return self.tEvt['event']

def setup_default_chart(trace_formatter=None, spy_formatter=None):
  if trace_formatter is None and spy_formatter is None:
    hsm = Hsm()
  if trace_formatter is None:
    hsm = Hsm(trace_formatter, None)
  else:
    hsm = Hsm(None, spy_formatter)

  hsm = Hsm( trace_formatter, spy_formatter )

  hsm.add_state( "d",    d,  None )
  hsm.add_state( "d1",   d1,  d    )
  hsm.add_state( "d11",  d11,  d1   )
  hsm.add_state( "d2",   d2,  d    )
  hsm.add_state( "d21",  d21,  d2   )
  hsm.add_state( "d211", d211, d21  )

  return hsm

def initialize_reporting_log():
  global hsm_reporting_log
  hsm_reporting_log = []
  print ""


def test_that_trace_is_on():
  hsm = setup_default_chart()

def spy_formatter( time, state, event, payload=None, chart=None ):
  return "spy(%s-%s)" % (state, event)

def trace_formatter( time, state_n_0, state_n_1, event, payload=None, chart=None ):
  return "trace(%s-%s-%s)" % (state_n_0, state_n_1, event)

def result(formatted_string):
  inside_brackets = re.search('\((.+)\)', formatted_string )
  items = inside_brackets.group(1).split('-')
  return items

def fn_confirm_results_match(fs1, fs2):
  r = True
  r &= (result(fs1)[0] == result(fs2)[0])
  r &= (result(fs1)[1] == result(fs2)[1])
  return r


def collections_match( collection_1, collection_2, fn_to_test_with ):
  """Match collections, given a testing function"""
  r = True
  r &= len(collection_1) == len(collection_2)

  if r == False:
    #import pdb;pdb.set_trace()
    pass

  for index, item in enumerate(collection_1, start=0):
    string_1 = item
    try:
      string_2 = collection_2[index]
    except:
      import pdb;pdb.set_trace()
      a = 1
    r &= fn_to_test_with( string_1, string_2 )
    if r == False:
      #import pdb;pdb.set_trace()
      pass

  return r

def test_start():
  initialize_reporting_log()
  global hsm_reporting_log
  hsm = setup_default_chart( trace_formatter, spy_formatter )
  hsm.live_chart_reflection = False
  hsm.live_spy              = False

  # run the state chart
  hsm.trigger_start("d")
  # confirm that the our locally defined logs match those generated within the
  # hsm class itself
  test_chart_self_reporting_spy = hsm_reporting_log
  hsmbase_spy_trace               = hsm.spy()
  # pp.pprint( test_chart_self_reporting_spy )
  # pp.pprint( hsmbase_spy_trace )
  assert collections_match(test_chart_self_reporting_spy, hsmbase_spy_trace, fn_confirm_results_match) == True

def test_with_event_a():
  initialize_reporting_log()
  global hsm_reporting_log
  hsm = setup_default_chart( trace_formatter, spy_formatter )
  hsm.live_chart_reflection = False
  hsm.live_spy              = False

  # run the state chart
  hsm.trigger_start("d")
  hsm.trigger_event("a")

  # confirm that the our locally defined logs match those generated within the
  # hsm class itself
  test_chart_self_reporting_spy = hsm_reporting_log
  hsmbase_spy_trace               = hsm.spy()
  # pp.pprint( test_chart_self_reporting_spy )
  # pp.pprint( hsmbase_spy_trace )
  assert collections_match( test_chart_self_reporting_spy, hsmbase_spy_trace, fn_confirm_results_match ) == True
def test_with_event_a_b():
  initialize_reporting_log()
  global hsm_reporting_log
  hsm = setup_default_chart( trace_formatter, spy_formatter )
  hsm.live_chart_reflection = False
  hsm.live_spy              = False

  # run the state chart
  hsm.trigger_start("d")
  hsm.trigger_event("a")
  hsm.trigger_event("b")

  # confirm that the our locally defined logs match those generated within the
  # hsm class itself
  test_chart_self_reporting_spy = hsm_reporting_log
  hsmbase_spy_trace               = hsm.spy()
  #pp.pprint( test_chart_self_reporting_spy )
  #pp.pprint( hsmbase_spy_trace )
  assert collections_match(test_chart_self_reporting_spy, hsmbase_spy_trace, fn_confirm_results_match) == True

def test_with_events_a_b_c_d_e_f_g_h_g_f_e_d_c_b_a():
  initialize_reporting_log()
  global hsm_reporting_log
  hsm = setup_default_chart(trace_formatter, spy_formatter)
  hsm.live_chart_reflection = False
  hsm.live_spy              = False

  # run the state chart
  hsm.trigger_start("d")
  hsm.trigger_event("a")
  hsm.trigger_event("b")
  hsm.trigger_event("c")
  hsm.trigger_event("d")
  hsm.trigger_event("e")
  hsm.trigger_event("f")
  hsm.trigger_event("g")
  hsm.trigger_event("h")
  hsm.trigger_event("g")
  hsm.trigger_event("f")
  hsm.trigger_event("e")
  hsm.trigger_event("d")
  hsm.trigger_event("c")
  hsm.trigger_event("b")
  hsm.trigger_event("a")

  # confirm that the our locally defined logs match those generated within the
  # hsm class itself
  test_chart_self_reporting_spy = hsm_reporting_log
  hsmbase_spy_trace               = hsm.spy()
  #pp.pprint( test_chart_self_reporting_spy )
  assert collections_match( test_chart_self_reporting_spy, hsmbase_spy_trace,
      fn_confirm_results_match ) == True
  assert collections_match( expected_spy(), hsmbase_spy_trace, fn_confirm_results_match )
  pp.pprint( hsmbase_spy_trace )
  hsm.clear_spy()

def test_reset():
  expected_reset_path = [ 'spy(d-entry)',
                          'spy(d-init)',
                          'spy(d2-entry)',
                          'spy(d2-init)',
                          'spy(d21-entry)',
                          'spy(d211-entry)',
                          'spy(d-reset)',
                          'spy(d211-exit)',
                          'spy(d21-exit)',
                          'spy(d2-exit)',
                          'spy(d-exit)',
                          'spy(d-entry)',
                          'spy(d-init)',
                          'spy(d2-entry)',
                          'spy(d2-init)',
                          'spy(d21-entry)',
                          'spy(d211-entry)']
  initialize_reporting_log()
  global hsm_reporting_log
  hsm = setup_default_chart(trace_formatter, spy_formatter)
  hsm.live_chart_reflection = False
  hsm.live_spy              = False
  print "resetting here!!!"
  hsm.trigger_start("d")
  #hsm.clear_spy()
  hsm.trigger_event("reset")
  assert collections_match( hsm.spy(), expected_reset_path, fn_confirm_results_match )


def test_get_substates():
  hsm = setup_default_chart(trace_formatter, spy_formatter)
  def get_state_name(hsm_dict):
    return hsm_dict['name']

  def test_with(target, search_term):
    result = hsm.on_substates(get_state_name, search_term)
    for state in target:
      assert( state in result )

  test_with(['d211', 'd11', 'd2', 'd21', 'd1'], 'd')
  test_with(['d11'], 'd1')
  test_with(['d21', 'd21'], 'd2')
  test_with(['d211'], 'd21')
  test_with([], 'd211')
  test_with([], 'd11')
  test_with([], 'd11111111111111111111111')

  assert( hsm.get_substate_functions('d1') == [d11] )
  assert( hsm.get_substate_names('d1') == ['d11'] )
