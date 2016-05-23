import pprint
import inspect
from hsmbase import Hsm
from functools import wraps

ppp = pprint.PrettyPrinter(indent=2)
def pp(thing):
  ppp.pprint(thing)

class SignalCatch(object):
  def __init__(self, **kwargs):
    self.with_history = False
    if 'event' in kwargs:
      self.name = kwargs['event']
    if 'handler' in kwargs:
      self.handler = kwargs['handler']
    if 'goto' in kwargs:
      self.goto = kwargs['goto']
    if 'trans' in kwargs:
      self.goto = kwargs['trans']
    if 'blocking' in kwargs:
      self.blocking = kwargs['blocking']

class Payload(object):
  def __init__(self, **kwargs):
    if 'payload' in kwargs:
      self.payload = kwargs['payload']

  def pp(self):
    pp(self.payload)

class State(object):
  def __init__(self, **kwargs):
    if 'name' in kwargs:
      self.name = kwargs['name']

    self.name             = kwargs['name']
    self.events          = {}
    self.history_observer = None

    # These attributes will be used by the handler for easy access to the event
    # and payload of the event that caused them to be called in the first place
    self.event  = None
    self.payload = None

    self.entry_handler = self.default_entry_handler
    self.exit_handler  = self.default_exit_handler
    self.init_handler  = self.default_init_handler

    self.events["entry"] = SignalCatch(
      event      = "entry",
      handler     = self.entry_handler,
      goto        = None,
      blocking    = True)

    self.events["exit"] = SignalCatch(
      event      = "exit",
      handler     = self.exit_handler,
      goto        = None,
      blocking    = True)

    self.run = self.dispatch_container
    self.dynamic_dispatcher = None

  # The purpose of this function is to keep a constant address
  # if the user calls catch over and over, the dispatcher_generation will make
  # new functions, with different addresses.  Since the hsm base, tracks keys
  # based on function addresses, it will lose track of things if we don't
  # provide a constant address for each space.
  def dispatch_container(self, chart):
    return self.dynamic_dispatcher(chart)

  def history_observer(chart):
    self.latest_history = chart.rCurr

  def compile(self, chart):
    self.dynamic_dispatcher = self.dispatcher_generation(chart)
    return self.run

  def dispatcher_generation(self, chart):
    state = self
    def run(chart):
      payload = None
      event_name = chart.tEvt['event']

      if 'payload' in chart.tEvt :
        payload = chart.tEvt['payload']
      
      chart.event = event_name
      chart.payload = payload
      chart.current                     = {}
      chart.current['state']            = state.name
      chart.current['event']           = event_name
      chart.current['state_reflection'] = state
      chart.current['payload']          = payload
      # what would have been 'self' in a static state chart is now called 'chart'

      if( event_name == "reflect"):
        return state.name # return our state name

      if event_name in state.events:
        event_catcher = state.events[event_name]
        if callable(event_catcher.handler):
          event_catcher.handler(chart)
        if event_catcher.goto:
          handler = chart.registry[event_catcher.goto]
          if event_name == "init":
            chart.state_start(handler)
          else:
            chart.goto(handler)
        if event_catcher.blocking:
          return 0

      # if we didn't handle it, or block the event, pass it out to the superstate
      return event_name
    return run

  def has_event(self, event_name):
    result = False
    if event_name in self.events:
      result = True
    return result

  def set_handler_for_event(chart, event, handler ):
    self.events[event] = handler

  def create(self,**kwargs):
    spec = kwargs
    event = spec['event']
    handler = spec['handler']
    return self

  def reflector(*rargs, **dkwargs):
    def reflector_(func):
      @wraps(func)
      def snitch(self, *args, **kwargs):
        if 'snitch' in dkwargs.keys():
          if dkwargs['snitch'] is True:
            caller = inspect.stack()[1][4][0]
            import re
            caller_function = re.search("[ ]+(.+?)\(", caller).group(1)
            pp("called from " + caller_function)
      return snitch
    return reflector_

  def catch(self, **kwargs):
    # default behavior
    event   = None
    handler  = None
    goto     = None
    blocking = True
    if 'event' in kwargs:
      event = kwargs['event']
    if 'handler' in kwargs:
       handler = kwargs['handler']
    if 'goto' in kwargs:
       goto = kwargs['goto']
    if 'blocking' in kwargs:
       blocking = kwargs['blocking']

    if event == None:
      raise "you need to specify a event for catch"

    self.events[event] = SignalCatch(event=event,
                                         handler=handler,
                                         goto=goto,
                                         blocking=blocking)
    if goto != None:
      goto_parsed = goto.split(".")
      if len(goto_parsed) == 2:
        if goto_parsed[1] == "history":
          # you will place this api in the registry
          pass
    return self

  # We don't need the reflector, it was originally made because I couldn't
  # figure out how to test something.  Leaving it here as example of how to use
  # decorators in this package
  @reflector(snitch=False)
  def default_exit_handler(state,chart):
    return 0

  def default_entry_handler(state, chart):
    return 0

  def default_init_handler(state,chart):
    return 0

class HsmFactory(object):

  # def t( time, state_n_0, state_n_1, event ):
  #   return "trace(%s-%s-%s)" % (state_n_0, state_n_1, event)

  # def s( time, state, event ):
  #   return "spy(%s-%s)" % (state, event)
  def __init__(self,**kwargs):
    self.states          = []
    self.spy_formatter   = None
    self.trace_formatter = None

    if 'trace_formatter' in kwargs:
      self.trace_formatter = kwargs['trace_formatter']

    if 'spy_formatter' in kwargs:
      self.spy_formatter = kwargs['spy_formatter']

    self.hsm  = Hsm(trace_formatter=self.trace_formatter,
        spy_formatter=self.spy_formatter)

    self.name = kwargs['name']
    self.hsm.name = self.name
    pass

  def has_state(self,state):
    result = False
    for state_obj in self.states:
      if state_obj.name is state:
        result = True
        break
    return result

  def register_handler(self, state, handler ):
    handler.chart = self
    if state in self.states:
      self.states[state].set_handler_for_event(self, handler.event, handler )

  def create(self, state):
    handled   = False
    new_state = None
    for existing_state in self.states:
      if existing_state.name is state:
        print "this was defined before, we are going to overwrite it"
        new_state = State(name=state)
        existing_state = new_state
        handled = True

    if not handled: # yet
      new_state = State(name=state)
      self.states.append(new_state)

    return new_state

  def state(self,name):
    state = None
    for state_obj in self.states:
      if state_obj.name is name:
        state = state_obj
        break
    return state

  def spy(self):
    return self.hsm.spy()

  def trace(self):
    return self.hsm.trace()

  def history_of_substate(self, hsm_dict_item):
    if callable(hsm_dict_item['fn']):
      self.history = hsm_dict_item['fn']
      self.hsm.registry[hsm_dict_item['api']] = hsm_dict_item['fn']

  def nest(self, **kwargs):
    """Upon nesting a state, we need iterate through our entire state chart
    """
    state_name = kwargs["state"]

    state_dispatcher = self.state(state_name).compile(self.hsm)
    parent_name = kwargs["parent"]
    if parent_name is None:
      self.hsm.add_state(state_name,state_dispatcher,None)
    else:
      parent_dispatcher = self.state(parent_name).compile(self.hsm)
      self.hsm.add_state(state_name,state_dispatcher,parent_dispatcher)

    if 'history' in kwargs:
      # mark up the state chart -- on each call to nest, we will re-organize the
      # transition to history, because we don't know how many time our client
      # will be nesting new states with this method
      api = "%s.history" % state_name
      self.hsm.history.add((self.history_of_substate,state_name,api))

    if len(self.hsm.history) != 0:
      # more than one item can register itself with a history
      # the later items take precedence over older items
      for trans_to_history_super_state in reversed(list(self.hsm.history)):
        observer  = trans_to_history_super_state[0]
        name      = trans_to_history_super_state[1]
        api       = trans_to_history_super_state[2]
        substates = self.hsm.get_substate_functions(name)

        for substate in substates:
          dict_item = self.hsm.hsm_dict[substate]
          #import pdb;pdb.set_trace()
          dict_item["register_entry_with"] = observer
          dict_item["api"]                 = api

      # import pdb;pdb.set_trace()
      # for state in substates:
      #   self.hsm
    # 
    # 1) get the substates
    # 1 
    # 2) in each of these substates add a history observer its set of history
    #    observers
    # self.history = kwargs['history']
    # 1) Iterate through the reversed history set
    # 2) pop the last item
    # 1) get its substates: hsm.get_substate_functions('d1') == [d11]
    # 2) get all of its substates to have its observer: chart.history_observer = self.history_of_substate
    # 3) augment this state with self.history, which is obtained from the
    #    observer -- which return something that can be called with hsmbase transition methods
    return self
  def trigger_start(self, state, **kwargs):
    self.hsm.trigger_start(state, **kwargs)

  def trigger_event(self, state, **kwargs):
    self.hsm.trigger_event(state, **kwargs)

  def clear_spy(self):
    self.hsm.clear_spy()

  def post_event(self,**kwargs):
    return self.hsm.post_event(**kwargs)

  def dis(self, event):
    return self.hsm.dis(event)

  def post_one_shot(self,**kwargs):
    return self.hsm.post_event(**kwargs)

  def live_spy(self, bool):
    self.hsm.live_spy = bool

  def live_trace(self, bool):
    self.hsm.live_trace = bool

  def cancel_event(self, event):
    self.hsm.cancel_event(event)

  def defer(self, event, **kwargs):
    self.hsm.defer(event, **kwargs)

  def refer(self, event, **kwargs):
    self.hsm.refer(event, **kwargs)

  def augment(self, other):
    self.hsm.augment(other=other.hsm, name=other.name, relationship='mutual')
    return self
