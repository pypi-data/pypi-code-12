from hsmbase import Hsm
from functools import wraps
import inspect
import pprint

ppp = pprint.PrettyPrinter(indent=2)
def pp(thing):
  ppp.pprint(thing)

class Channel(object):
  __channels__ = {}
  def __init__(self, **kwargs):
    if 'name' in kwargs:
      self.name = kwargs['name']
      self.events = {}

  def subscribe(self, event, publish_metholology):
    if event in self.events:
      event_array = self.events[event]
      pass

  def publish(self, event):
    # write your complicated publisher here
    pass

  # merge two channels, with a list of events which will be shared between them
  def merge(self, other, filter):
    pass

class Channels(object):
  __channels__ = {}

  def channels(self):
    names = []
    for k, v in self.__channels__.iteritems():
      names.append(k) 
    return names
