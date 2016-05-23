# -*- coding: utf-8 -*-
"""This is the miros module for creating statecharts"""
import time
import datetime
import copy
from Queue import Queue
from threading import Thread
from collections import deque  # This is used for the trace
                                         # functionality. Traces are good for
                                         # testing and documenting your
                                         # statechart.
from copy import *
from trace import Trace  # Use to store information about what is
                               # happening in the hsmbase
import inspect
import pprint
ppp = pprint.PrettyPrinter(indent=2)
def pp(thing):
  ppp.pprint(thing)
__author__  = "Scott Volk <impregnable.quebec@gmail.com>"
__date__    = "7 May 2016"
__version__ = "$Revision: 1.0 $"
__credits__ = """Miro Samek/Paul Montgomery/Tom Schmit

  Hsmbase - A Python module that implements a Hierarchical State Machine (HSM)
  class (i.e. one that implements behavioral inheritance).

  It is based on the excellent work of Miro Samek (hence the module name
  "miros"). This implementation closely follows an older C/C++
  implementation published in the 8/00 edition of "Embedded Systems"
  magazine by Miro Samek and Paul Montgomery under the title "State
  Oriented Programming". The article and code can be found here:
  http://www.embedded.com/2000/0008.

  A wealth of more current information can be found at Miro's well kept
  site: http://www.state-machine.com/.

  As far as I know this is the first implementation of Samek's work in
  Python. It was tested with Python 2.5

  It is licensed under the same terms as Python itself.  """

class PostEvent(Thread):
  FOREVER = -1
  POSTED_DEFAULT_DELAY = 0.5

  def __init__(self, q, **kwargs):
    Thread.__init__(self)
    self._running  = True
    self.payload   = None
    self.period     = PostEvent.POSTED_DEFAULT_DELAY
    self.times     = 1
    self.q         = q
    self.deferred  = False

    if 'times' in kwargs:
      self.times = kwargs['times']

    if 'period' in kwargs:
      self.period = kwargs['period']

    if 'event' in kwargs:
      self.event = kwargs['event']

    if 'payload' in kwargs:
      self.payload = kwargs['payload']

    if 'deferred' in kwargs:
      self.deferred = kwargs['deferred']

    if 'tick_name' in kwargs:
      self.tick_name = kwargs['tick_name']
    else:
      self.tick_name = 'tik'

  def terminate(self):
    self._running = False

  def run(self):

    def deliver_event(thread_count):
      if self.payload is not None:
        self.payload[self.tick_name] = thread_count
        self.q.put((self.event,self.payload))
      else:
        self.payload = {}
        self.payload[self.tick_name] = thread_count
        self.q.put((self.event,self.payload))
      time.sleep(self.period)

    # This allows us to create a perioded event
    # This is useful if you want to create a oneshot
    if self.deferred is True:
      time.sleep(self.period)
      self.deferred = False

    if self.times >= 0:
      for thread_count in range(self.times):
        deliver_event(thread_count)
        if self._running is False:
          return
      self._running = False
    else:
      thread_count = 0
      while(1):
        deliver_event(thread_count)
        thread_count += 1
        if self._running is False:
          break

class PostEvents(object):
  def __init__(self,**kwargs):
    self.events = []
    self.q      = Queue()
    self.events.append(PostEvent(self.q, **kwargs))

  def append(self,**kwargs):
    self.events.append(PostEvent(self.q, **kwargs))
    return self

  # If we want to append an event directly, rather than by creating it with our
  # constructor -- we will do this with one shots, or events that are created on
  # the fly by the state chart
  def append_event(self,producer):
    # give the producer access to our queue
    producer.q = self.q
    self.events.append(producer)
    # returned the updated producer
    return producer

  def start(self):
    for post in self.events:
      post.start()

  def terminate(self):
    for post in self.events:
      post.terminate()

  def remove(self, event):
    for post in self.events:
      if post.event is event:
        post.terminate()
        post.join()

class Consumer(Thread):
  def __init__(self,fn,producers):
    Thread.__init__(self)
    self._running = True
    self.q = producers.q
    self.watched_threads = producers.events
    self.producers = producers
    self.fn = fn
    producers.start()

  # We will use this method when the state chart is creating producing events
  # after it has been initiated (like when it wants to trigger a oneshot or a
  # perioded series of pulsed events)
  def append(self, producer):
    producer = self.producers.append_event(producer)
    self.watched_threads.append(producer)
    producer.start()

  def terminate(self):
    self._running = False
    self.producers.terminate()

  def threads_alive(self):
    threads_alive = False
    for thread in self.watched_threads:
      threads_alive |= thread.is_alive()
    return threads_alive

  def run(self):
    threads_alive = self.threads_alive()
    while True:
      if self.q.empty() is not True:
        item = self.q.get()
        self.fn(item)
        self.q.task_done()
      else:
        time.sleep(0.1)
        threads_alive = self.threads_alive()
        if threads_alive is not True:
          return

class HsmBaseException(Exception):
  def __init__(self,value):
    self.value = value
  def __str__(self):
    return repr(self.value)

class TreeNode(object):
  def __init__(self, d):
    """
    A tree node has sub_states
    """

    self.d = d
    self.sub_states = []
  def add_sub_state(self, obj):
    self.sub_states.append(obj)

class Tree:
  def __init__(self):
    """
    If you build a tree you can:
      * get all of the of the nodes below a given location on the tree:
        get_sub_nodes
      * get a given node, if you have its data:
        get_node

    '''Example'''
      tr = Tree()
      a = tr.root

      b = TreeNode("B")
      c = TreeNode("C")
      d = TreeNode("D")
      e = TreeNode("E")
      f = TreeNode("F")

      a.add_child(b)
      b.add_child(c)
      b.add_child(d)
      b.add_child(e)
      e.add_child(f)

      n = a
      ns = map(lambda x: print(x.d), tr.get_sub_nodes(n))
      print ns # => "B C D E F"
    """
    self.root = TreeNode("ROOT")

  def get_sub_nodes(self, n=None):
    """
    Get all nodes below n in the tree
    """
    leafs = set([])
    if n is None:
      n = self.root
    def _get_leaf_ns(n):
      if n is not None:
        for n in n.sub_states:
          leafs.add(n)
          _get_leaf_ns(n)
    _get_leaf_ns(n)
    return list(leafs)

  def get_node(self,fn):
    """
    Return a node from a tree given it's data

      '''Example:'''
      tr = Tree()
      a = tr.root
      b = TreeNode("B")
      result = tr.get_node("B")
      assert( result == b ) # will pass
    """
    leafs = self.get_sub_nodes(self.root)
    for leaf in leafs:
      if fn(leaf.d):
        return leaf.d

class Hsm(object):

  """see __init__"""

  records      = 1000
  fifo_size    = 10
  ltrace       = Trace()
  HANDLED      = 0

  @classmethod
  def default_spy_formatter(cls, time, state, event, payload, chart=None):
    """
    The default trace formatter function, if the user did not provide one
    during object construction, see hsm.__init__ for details.
    """
    s = ""
    if payload is None:
      s = "df(%s-%s)" % (state, event)
    else:
      if callable(payload):
        import pdb;pdb.set_trace()
      s = "df(%s-%s-%s)" % (state, event, payload)
    return s

  @classmethod
  def default_trace_formatter(cls, time, state_n_0, state_n_1, event, payload=None, chart=None):
    """
    The default trace formatter function, if the user did not provide one
    during object construction, see __init__ for details.
    """
    s = ""
    if payload is None:
      payload = None
      s = "%s->%s(%s)" % (state_n_0, state_n_1, event)
    else:
      s = "%s->%s(%s:%s)" % (state_n_0, state_n_1, event, payload)
    return s

  def __init__(self, trace_formatter=None, spy_formatter=None):
    """
    Hsm - A Python module that implements a Hierarchical State Machine (HSM)
    class (i.e. one that implements behavioral inheritance).

    Args:
      trace_formatter(Optional[fn]): Defaults to None.  A function which can be
      used to overload the behavior of the default trace output.

      spy_formatter(Optional[fn]): Defaults to None. A function which can be
      used to overload the behavior of the default spy output.

    ``Example``

      def t( time, state_n_0, state_n_1, event ):
        return "trace(%s-%s-%s)" % (state_n_0, state_n_1, event)

      def s( time, state, event ):
        return "spy(%s-%s)" % (state, event)

      hsm = Hsm(trace_formatter=t, spy_formatter=s)

      # This would result in the following format, given the following arbitrary
      # state transitions:

      hsm.trace() # => t("top-d21-entry")
      # or
      hsm.spy()   # => "s(top-entry)"
                  # => "s(top-init)"
                  # .
                  # .
    """
    self.hsm_dict        = {}
    self.registry        = {}
    self.spy_buffer      = deque(maxlen = self.records)
    self.trace_buffer    = deque(maxlen = self.records)
    self.live_spy        = False
    self.live_trace      = False
    self.out_of_bounds   = False
    self.tEvt            = {}
    self.rCurr           = {}
    self.rNext           = {}
    self.rSource         = {}
    self.event_fifo      = Queue()
    self.init_fifo       = Queue()
    self.deferred_fifo   = Queue()
    self.searching       = False
    self.threads         = []
    self.report_missing  = True
    self.name            = ""
    self.trace_formatter = self.default_trace_formatter \
      if trace_formatter is None else trace_formatter

    self.spy_formatter = self.default_spy_formatter \
      if spy_formatter is None else spy_formatter

    self.producers = None
    self.consumer  = None

    self.history   = set([])

  def clear_spy(self):
    """
    clear the spy buffer
    """
    self.spy_buffer = deque(maxlen = self.records)

  def clear_trace(self):
    self.trace_buffer = deque(maxlen = self.records)

  def __spy__(self, state, event, payload=None):
    """
    Used to record the instantaneous state of a state
    chart
    """
    self.spy_buffer.append(Trace(state_n_0=None,
                                 state_n_1=state, event=event,
                                 payload=payload, chart=self.name))

    ts = time.time()
    dt = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S.%f')
    if self.live_spy:
      print self.spy_formatter(dt, state, event=event, payload=payload, chart=self.name)

  def __trace__(self, state, event, payload=None):
    """
    Used to record enough information that a trace can be
    reported to the user when the call the trace function.
    """
    if self.ltrace.state_n_0 is None:
        self.ltrace.state_n_0 = "__init__"

    if payload is None:
      payload = None

    ts = time.time()
    dt = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S.%f')

    self.trace_buffer.append(Trace(state_n_0=self.ltrace.state_n_0,
                                   state_n_1=state,
                                   event=event,
                                   payload=deepcopy(payload),
                                   chart=self.name))
    if self.live_trace:
      print self.trace_formatter(dt, self.ltrace.state_n_0, state, event, payload, self.name)
    self.ltrace.state_n_0 = state

  def __format_reflection__(self, log, formatter, *args):
    """
    Used to format a spy/trace reflection
    Uses maps the provided formatter against the log provided.
    If the size is specified, it only return the last <size> number of logs
    """
    if len(args) == 0:
      log_array = log
    else:
      log_array = log[-1*args[0]:]
    #else:
    #  log_array = log.get()

    formatted_list = map(formatter, log_array)
    return formatted_list

  def kill_threads(self):
    if self.consumer is not None:
      self.consumer.terminate()

  def trace(self, *args):
    """
    Used to return a formatted 'trace' (low detail) log of what happened to a
    state chart.  If the size is specified, it only return the last <size>
    number of trace items

    ``Example``
      # Given, 'chart' is a hsm which has seen some action
      # Here we print the last for trace events
      print(chart.hsm.trace(4)) #=> ['d11->d11(d)', 'd11->d211(c)',
                                     'd211->d211(b)', 'd211->d211(a)']

    A trace is a summarized list of the previous events which caused a change of
    state in the state chart.

    Each item in the list report on the initial state, the final state and the
    event that caused this transition.  In the above trace we see the last
    trace item is 'd211->d211(a)'.  From this, we can see that the state chart
    was in the 'd211' state when it received an 'a' event.  After it finished
    processing 'a' it settled back into the 'd211' state.  To view what occurred
    in greater detail, you can use the 'spy' method.
    """
    return self.__format_reflection__(self.trace_buffer,
                                      self.format_trace_trace,
                                      *args)
  def spy(self, *args):
    """
    Used to return a formatted 'spy' (high detail) log of what happened to a
    state chart.  If the size is specified, it only return the last <size>
    number of spy items.

    ``Example``
      # Given, 'chart' is a hsm which has seen some action
      # Here we print the last for spy events
      print(chart.hsm.spy(4)) #=> ['df(d21-exit)', 'df(d21-entry)',
                              #    'df(d21-init)', 'df(d211-entry)']

    A spy is a complete list of events that happened to the state chart.

    Each item in the list report on the state and the event that caused the
    state to process the action.  Consider the last event in the above spy
    output example, 'df(d211-entry)'.  Here we see that the state chart entered
    the d211 state.  A call to spy can output a lot of glandular detail about
    what has happened to your state chart, if you would like to see less detail,
    using the trace method instead.
    """
    return self.__format_reflection__(self.spy_buffer,
                                      self.format_spy_trace,
                                      *args)
  def format_spy_trace(self, __trace__):
    """Format the ```spy``` trace for the hsm object"""
    return self.spy_formatter(__trace__.datetime, __trace__.state_n_1,
                              __trace__.event,
                              __trace__.payload,
                              __trace__.chart)

  def format_trace_trace(self, __trace__):
    """Format the ```spy``` trace for the hsm object"""
    return self.trace_formatter(__trace__.datetime,
                              __trace__.state_n_0,
                              __trace__.state_n_1,
                              __trace__.event,
                              __trace__.payload,
                              __trace__.chart)

  def __set_sub_states__(self, hsm_dict, parent=None):
    """
    Put sub_state information, as a list, into the hsm_dict
    """
    for key, _dict in hsm_dict.iteritems():
      _dict['sub_states'] = set([])

    def _get_sub_states(parent):
      for key, _dict in hsm_dict.iteritems():
        parent_fn = _dict['super_state']
        if parent_fn is parent:
          if parent_fn is not None:
            hsm_dict[parent_fn]['sub_states'].add(key)
          _get_sub_states(key)
        else:
          pass
    _get_sub_states(parent)

  def add_state(self, state_name, state_function, super_state):
    """
    Add a new state to the HSM. Specifies name, handler function, parent
    state, and initializes an empty cache for toLca. These are added to Hsm as a
    sub-table that is indexed by a reference to the associated handler function.
    Note that toLca is computed when state transitions. It is the number of
    levels between the source state and the least/lowest common ancestor is
    shares with the target state.
    """
    self.hsm_dict[state_function] = dict(name   = state_name,
                                    handler     = state_function,
                                    super_state = super_state,
                                    toLcaCache  = {}
                                    )
    self.hsm_dict[state_function]['fn'] = state_function
    self.registry[state_name] = state_function
    # add sub_states to the hsm dictionary
    self.__set_sub_states__(self.hsm_dict)
    if super_state is None:
      self.ltrace.state_n_0 = state_name

  def __hsm_dict_to_tree__(self, hsm_dict, state_tree=Tree()):
    """
    Create a tree within the hsm_dict
    """
    self.__set_sub_states__(hsm_dict, None)
    root = state_tree.root
    for i in hsm_dict.keys():
      hsm_dict[i]['node'] = TreeNode(hsm_dict[i])
      hsm_dict[i]['key']  = i
    for i in hsm_dict.keys():
      _dict = hsm_dict[i]
      if _dict['super_state'] is None:
        root.add_sub_state(_dict['node'])
      for sub_state in _dict['sub_states']:
        _dict['node'].add_sub_state(hsm_dict[sub_state]['node'])
    return state_tree

  def __remove_tree__(self, hsm_dict):
    """
    Remove the tree information from the hsm_dict struct
    We use this function to ensure that the tree is re-created on each nest
    call, and destroyed afterwards so we don't end up with an residue
    """
    for i in hsm_dict.keys():
      hsm_dict[i].pop('node', None)
      hsm_dict[i].pop('key', None)
      #hsm_dict[i].pop('fn', None)

  def get_substate_functions(self, state_name):
    def get_state_function(hsm_dict):
      return hsm_dict['fn']
    return self.on_substates(get_state_function, state_name)

  def get_substate_names(self, state_name):
    def get_state_name(hsm_dict):
      return hsm_dict['name']
    return self.on_substates(get_state_name, state_name)

  def substates(self, state_name):
    """ This will return a substate dict of the hsm_dict
        example:
        hsm[d1]   = {'name':"d1",   'super_state':_top}
        hsm[d11]  = {'name':"d11",  'super_state':d1}
        substate("d1") => {'name':"d11",  'super_state':d1}
    """
    substates = []
    key = None
    state_tree = self.__hsm_dict_to_tree__(self.hsm_dict)
    for state_fn in self.hsm_dict.keys():
      if state_name is self.hsm_dict[state_fn]['name']:
        key = self.hsm_dict[state_fn]['key']
    if key in self.hsm_dict and "node" in self.hsm_dict[key]:
      n = self.hsm_dict[key]["node"]
      nodes = state_tree.get_sub_nodes(n)
      map(lambda x: substates.append(x.d), state_tree.get_sub_nodes(n))
      self.__remove_tree__(self.hsm_dict)
    else:
      substate = []

    return substates

  def on_substates(self, fn, state_name):
    """
    Perform a function on the substates

    ``Example``:
    def get_state_name(hsm_dict_item):
      return hsm_dict_item['name']

    hsm[d1]  = {'name':"d1",   'super_state':_top}
    hsm[d11] = {'name':"d11",  'super_state':d1}
    on_substates("d1") => "d11"
    """
    results = []
    states = self.substates(state_name)
    map(lambda x: results.append(fn(x)), states)
    return results
    def dump(self):
      """Display parent-child relationship of states"""
      # self.pp.pprint(self.hsm_dict)
      print
      for state in self.hsm_dict:
        print "State: " + self.hsm_dict[state]['name'] + "\t", self.hsm_dict[state]

  def split(self):
    for k,v in self.hsm_dict.iteritems():
      pp(k)
      pp(v)

  def trigger_start(self, rTarget, **kwargs):
    payload = None
    if 'payload' in kwargs:
      payload = kwargs['payload']
    self.init_fifo.put((rTarget, payload))
    self.__trigger_start__()
    return self

  def trigger_event(self, event, **kwargs):
    payload = None
    if( "payload" in kwargs ):
      payload = kwargs['payload']
    self.event_fifo.put((event, payload))
    self.__trigger_event__()

  def dis(self, event):
    event = None
    payload = None
    if( "payload" in event ):
      payload = event['payload']
    if( "event" in event ):
      event = event['event']
    self.event_fifo.put((event, payload))
    if self.searching is False:
      self.__trigger_event__()

  def defer(self, event, **kwargs):
    payload = None
    if( "payload" in kwargs ):
      payload = kwargs['payload']
    self.deferred_fifo.put((event, deepcopy(payload)))

  def recall(self):
    if(self.deferred_fifo.empty() is not True):
      self.event_fifo.put(self.deferred_fifo.get())

  def __record_entry_history__(self, rEntry):
    """
    Record our entry history with an observer.  For this method to work the
    rCurr must be set before we call it
    """
    if("register_entry_with" in rEntry.keys()):
      observer = rEntry["register_entry_with"]
      #import pdb;pdb.set_trace()
      observer(rEntry);

  def __trigger_start__(self):
    self.searching = True
    rTarget,payload = self.init_fifo.get()
    """
    Start an HSM.  Enters and starts the topmost state.  (see hsm.add_state for
    more details about the top most state)
    """
    rTarget = self.registry[rTarget]
    self.tEvt = {'event':"entry", 'payload':None}

    if( payload is not None ):
      self.tEvt['payload'] = payload
    # expandable table containing event parameters sent to HSM
    self.ltrace.event = "entry"
    self.rCurr = self.hsm_dict[rTarget]
    self.__spy__(self.rCurr['name'], self.tEvt['event'], self.tEvt['payload'])
    # self.pp.pprint(self.rCurr)
    self.rNext = 0
    # handler for top sets initial state
    self.rCurr['handler'](self)
    self.__record_entry_history__(self.rCurr)
    # get path from initial state to top/root state
    while True:
      self.tEvt['event'] = "init"
      self.rCurr['handler'](self)
      if self.rNext == 0:
        break
      self.__spy__(self.rCurr['name'], self.tEvt['event'], self.tEvt['payload'])
      entryPath = []
      s = self.rNext
      # while s != self.rCurr and s['super_state'] != None:
      while s != self.rCurr:
        # trace path to target
        entryPath.append(s)
        try:
          s = self.hsm_dict[s['super_state']]
        except:
          #import pdb;pdb.set_trace()
          a = 1
        # s = self.hsm_dict.get(s['super_state'], None)
      # follow path in reverse calling each handler
      self.tEvt['event'] = "entry"
      entryPath.reverse()
      for h in entryPath:
        self.__spy__(h['name'], self.tEvt['event'], self.tEvt['payload'])
        # retrace entry from source
        # self.pp.pprint(h)
        h['handler'](self)
        self.__record_entry_history__(h)
      self.rCurr = self.rNext
      self.rNext = 0

    # Start up the producers thread if we haven't done so before
    # This will start up all of the producer threads which will start to provide
    # a heart beat for your chart
    if self.producers is not None and self.consumer is None:
      self.consumer = Consumer(self.__post_to_event_fifo__, self.producers)
      self.consumer.start()

    self.__trace__(self.rCurr['name'], self.ltrace.event, self.tEvt['payload'])
    self.tEvt['payload'] = None
    self.init_fifo.task_done()
    self.searching = False

  def __post_to_event_fifo__(self, item):
    self.event_fifo.put(item)
    self.__trigger_event__()

  def post_fifo(self, **kwargs):
    event = None
    payload = None
    if 'event' in kwargs:
      event = kwargs['event']

    if 'payload' in kwargs:
      payload = kwargs['payload']

    self.producers.q.put((event,payload))

  def cancel_event(self, event):
    self.producers.remove(event=event)

  def post_event(self, **kwargs):
    if self.consumer is None:
      if self.producers is None:
        self.producers = PostEvents(**kwargs)
      else:
        self.producers.append(**kwargs)
    # the consumer has been built, we will have to append to it
    else:
      new_event = PostEvent(None, **kwargs)
      self.consumer.append(new_event)
    return self.producers

  def __trigger_event__(self):
    self.searching = True
    event, payload = self.event_fifo.get()
    """Dispatch events"""
    self.tEvt = {'event':event, 'payload':None}
    if( payload is not None ):
      self.tEvt['payload'] = payload
    self.record_trace = False
    self.ltrace.event  = event
    s = self.rCurr
    self.ltrace.state_n_1 = self.rCurr['name']
    while True:
      # level of outermost event handler
      self.rSource = s
      self.tEvt['event'] = s['handler'](self)
      # processed?
      if self.tEvt['event'] == 0:
        # self.__spy__(s['name'], self.tEvt['event'])
        # state transition taken?
        # print self.rNext
        if self.rNext != 0:
          entryPath = []
          s = self.rNext
          while s != self.rCurr:
           # while s != self.rCurr and s['super_state'] != None:
            # trace path to target
            entryPath.append(s)
            if s['super_state'] is not None:
              s = self.hsm_dict[s['super_state']]
            else:
              s = self.rCurr
          if len(entryPath) is 0 and self.out_of_bounds is True:
            entryPath.append(s)
            self.out_of_bounds = False
          # follow path in reverse from LCA calling each handler
          self.tEvt['event'] = "entry"
          entryPath.reverse()
          for h in entryPath:
            self.__spy__(h['name'], self.tEvt['event'], self.tEvt['payload'])
            self.record_trace = True
            h['handler'](self)
            self.__record_entry_history__(h)
          self.rCurr = self.rNext
          self.rNext = 0
          while True:
            self.tEvt['event'] = "init"
            self.rCurr['handler'](self)
            if self.rNext == 0:
              break
            self.__spy__(self.rCurr['name'], self.tEvt['event'], self.tEvt['payload'])
            entryPath = []
            s = self.rNext
            while s != self.rCurr:
             # while s != self.rCurr and s['super_state'] != None:
              # record path to target
              entryPath.append(s)
              s = self.hsm_dict[s['super_state']]
            # follow path in reverse calling each handler
            self.tEvt['event'] = "entry"
            entryPath.reverse()
            for h in entryPath:
              self.__spy__(h['name'], self.tEvt['event'], self.tEvt['payload'])
              # retrace entry
              h['handler'](self)
              self.__record_entry_history__(h)
            self.rCurr = self.rNext
            self.rNext = 0
        # event processed
        break
      if s['super_state'] is not None:
        s = self.hsm_dict[s['super_state']]
      else:
        # Ignore this event, no states handle it
        # To turn off this report, change report_missing to False
        if self.report_missing:
          self.__spy__('ignored', self.tEvt['event'], self.tEvt['payload'])
          #print "%r is NOT handled" % self.tEvt
          self.searching = False
          return self.HANDLED
        self.event_fifo.task_done()
        self.tEvt['payload'] = None
    if self.record_trace is True:
      self.__trace__(self.rCurr['name'], self.ltrace.event, self.tEvt['payload'])
    self.tEvt['payload'] = None
    #deferred_event = self.fifo.pop()
    #if deferred_event is not None:
    #  self.trigger_event(deferred_event['event'], payload=deferred_event['payload'])
    if self.event_fifo.empty() is not True:
      self.__trigger_event__()
    self.searching = False
    return self.HANDLED

  def exit(self, toLca):
    """
    Exit the current states and all super_state states up to the LCA
    (lowest common ancenstor)
    """
    s = self.rCurr
    self.tEvt['event'] = "exit"
    while s != self.rSource:
      s['handler'](self)
      self.__spy__(s['name'], self.tEvt['event'], self.tEvt['payload'])

      s = self.hsm_dict[s['super_state']]
    while toLca != 0:
      toLca = toLca - 1
      s['handler'](self)
      self.record_trace = True
      self.__spy__(s['name'], self.tEvt['event'], self.tEvt['payload'])
      if s['super_state'] is not None:
        s = self.hsm_dict[s['super_state']]
      else:
        self.out_of_bounds = True
        toLca = 0
    # only exit this state if we are leaving this part of the chart entirely
    if self.out_of_bounds:
      if ( s['name'] in self.get_substate_names(s['name'] ) ) is not True \
           and s['name'] is not self.rSource['name']:
        s['handler'](self)
        self.__spy__(s['name'], self.tEvt['event'], self.tEvt['payload'])
        self.out_of_bounds = False
    self.rCurr = s

  def to_lca(self, Target):
    """Find number of levels to the least common ancestor."""
    toLca = 0
    if self.rSource == Target:
      return 1
    s = self.rSource
    while s is not None:
      t = Target
      while t is not None:
        if s == t:
          return toLca
        t = self.hsm_dict.get(t['super_state'], None)
      toLca = toLca + 1
      if s['super_state'] == None:
        self.out_of_bounds = True
      s = self.hsm_dict.get(s['super_state'], None)
    return self.HANDLED

  def goto(self, rTarget, **kwargs):

    if callable(rTarget) is False:
      rTarget = self.registry[rTarget]

    if( "payload" in kwargs ):
      self.tEvt['payload'] = kwargs['payload']

    """Transition to a new state (Cached Version)"""
    caller = inspect.stack()[1][3]  # hsm could be calling its super states
                                    # we aren't tracking this in this, so we can
                                    # just reference the call stack to find who
                                    # discovered the event
    #print "\nCurrent state: ", self.rCurr; print "Source state: ", self.rSource
    self.__spy__(caller, self.tEvt['event'], self.tEvt['payload'])

    # this is how you see the target
    if self.rCurr['toLcaCache'].get(self.tEvt['event'], None) == None:
      self.rCurr['toLcaCache'][self.tEvt['event']] = \
          self.to_lca(self.hsm_dict[rTarget])
    # self.pp.pprint(self.rCurr); print
    self.exit(self.rCurr['toLcaCache'][self.tEvt['event']])
    self.rNext = self.hsm_dict[rTarget]

  def state_start(self, Target):
    """Set the initial state of the the statechart"""
    self.rNext = self.hsm_dict[Target]

  def state_current(self):
    return self.rCurr

  def augment(self, **kwargs):
    """Used to add attributes to an hsm object

    Args:
      kwargs['other'](Mandatory other object): An another object for which you would
      like to add as an attribute of this object.

      kwargs['name'](Mandatory): The name that you would like to call this
      attribute, this argument must be a string

      kwargs['relationship'](Optional): Indicates if you want to also add this
      object as an attribute to the other class, using this object's name.  This
      option will only work if the other object also has an augment method that
      acts exactly the same as this one.

      ``Examples``
      alarm       = Hsm(); alarm.name       = "alarm"
      time_keeper = Hsm(); time_keeper.name = "time_keeper"
      alarm.augment(other=time_keeper, name="time_keeper")

      assert(alarm.time_keeper == time_keeper) # will be true

      inverter  = Hsm(); inverter.name = "inverter"
      networker = Hsm(); networker.name = "networker"
      inverter.augment(other=networker, name="net", relationship="mutual")

      assert(inverter.net == networker) # will be true
      assert(networker.inverter == inverter ) # will be true
    """

    relationship = None
    if("other" in kwargs ):
      other = kwargs['other']
    if("name" in kwargs ):
      name = kwargs['name']
    if("relationship" in kwargs ):
      relationship = kwargs['relationship']

    if hasattr(self, name ) is not True:
      setattr(self, name, other)
    else:
      pass
    if( relationship != None and relationship == "mutual"):
      other.augment( other=self, name=self.name, relationship=None )

