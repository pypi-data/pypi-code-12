from miros.channel import *
from miros.hsmfactory import *
from miros.hsmbase import Hsm
import pprint
import sys
import re
import inspect
import pytest
import pdb

class Example(object):
  observed_event  = None
  def __init__(self):
    self.observed_event = None
    pass

  def consumer(event):
    self.observed_event = event

class Example_1(Example):
  def __init__(self):
    self.observed_event = None

class Example_2(Example):
  def __init__(self):
    self.observed_event = None

def test_subscription():
  e1 = Example_1()
  e2 = Example_2()
  channel = Channel(name="connection_1")
  channel.subscribe("a", e1.consumer )
  channel.publish("a")
  #assert(e1.observed_event == "a")

