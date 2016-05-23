import time
import datetime
# to use this module:
# trace_1 = Trace(state_n_0 = "top",
#                 state_n_1 = "inner",
#                 event = "z" )
# trace_1.to_s # => [2016-04-04 09:41:23], [00] cTrig->z() top->inner
# or, if you don't want to name your arguments
# trace_2 = Trace("top",
#                 "inner",
#                 "l" )
# trace_2.to_s # => [2016-04-04 09:41:23], [00] cTrig->l() top->inner

class Trace(object):
  def __init__(self, state_n_0=None, state_n_1=None, event=None, payload=None, chart=None):
    ts = time.time()
    self.state_chart = "00"
    self.datetime    = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    self.state_n_0   = state_n_0
    self.state_n_1   = state_n_1
    self.event      = event

    if chart is None:
      chart = None
    self.chart = chart

    if payload is None:
      payload = None
    self.payload = payload

  def time(self):
    return self.datetime

  def state_n_0(self):
    return self.state_n_0

  def state_n_1(self):
    return self.state_n_1

  def event(self):
    return self.event

  def payload(self):
    return self.payload

  def chart(self):
    return self.chart

  def to_s(self):
    s = ""
    if self.payload is None:
      s = "[%s], [%s] cTrig->%s() %s->%s" % (self.datetime, self.state_chart, self.event, self.state_n_0, self.state_n_1)
    else:
      s = "[%s], [%s] cTrig->%s() %s->%s payload:" % (self.datetime, self.state_chart, self.event, self.state_n_0, self.state_n_1, self.payload)
    return s
