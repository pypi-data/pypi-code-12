from miros.trace import Trace
import pytest

def test_trace():
  trace = Trace("top", "inner","h")
  assert trace.state_n_0 == "top"
  assert trace.state_n_1 == "inner"
  assert trace.event == "h"
  #print trace.to_s()

  trace = Trace(state_n_0="top",
                state_n_1="inner",
                event="z")
  #print trace.to_s()
