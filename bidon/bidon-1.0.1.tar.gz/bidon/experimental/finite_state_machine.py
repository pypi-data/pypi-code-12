"""Contains the FiniteStateMachine class."""
from collections import namedtuple


__all__ = ["FiniteStateMachine"]


NodeType = namedtuple("NodeType", ["checker", "handler", "state"])


class FiniteStateMachine(object):
  """An implementation of a finite state machine."""
  def __init__(self, graph, initial_node_type, node_handler):
    """Construct the FiniteStateMachine instance.

    :graph: a dictionary of NodeType => Tuple[NodeType]
    :initial_node_type: the value last_node_type should be set to when parsing a new stream
    :node_handler: a function accepting (NodeType.handler(data), NodeType, raw_data)
    """
    self.graph = graph
    self.initial_node_type = initial_node_type
    self.handle = node_handler
    self.last_node_type = None

  def _handle_node(self, data):
    """Given a piece of data, check each node_type that the last_node_type can lead to and act using
    the first whose checker returns true.
    """
    next_options = self.graph[self.last_node_type]
    for node_type in next_options:
      checker, handler, *_ = node_type
      if checker(data):
        self.last_node_type = node_type
        self.handle(handler(data), node_type, data)
        return
    raise Exception("Unable to handle data: {}".format(data))

  def step(self, node):
    """Steps the machine up with a given node."""
    self._handle_node(node)

  def parse(self, nodes):
    """Given a stream of node data, try to parse the nodes according to the machine's graph."""
    self.last_node_type = self.initial_node_type
    for node_number, node in enumerate(nodes):
      try:
        self.step(node)
      except Exception as ex:
        raise Exception("An error occurred on node {}".format(node_number)) from ex
