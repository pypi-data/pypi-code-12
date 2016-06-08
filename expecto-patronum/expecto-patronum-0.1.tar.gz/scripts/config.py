# encoding: UTF-8

import os, sys, re, yaml, env

# make inheritance of dict correctly
class Playbook(object):

  def __init__(self, data, invoke):
    self.data = data
    self.invoke = invoke

  def _timeout(self):
    if self.data.get(self.invoke).get('timeout'):
      return self.data.get(self.invoke).get('timeout')
    if self.data.get('default'):
      return self.data.get('default').get('timeout')
    return env.TIMEOUT

  def _stdout(self):
    is_match = lambda x: re.match(r"true|1", x.lower())
    if self.data.get(self.invoke).get('stdout'):
      stdout = self.data.get(self.invoke).get('stdout')
      if is_match(str(stdout)):
        return stdout
    if self.data.get('default'):
      stdout = self.data.get('default').get('stdout')
      if is_match(str(stdout)):
        return stdout
    return env.STDOUT

  def _spawn(self):
    if self.data.get(self.invoke).get('spawn'):
      return self.data.get(self.invoke).get('spawn')
    return env.SPAWN

  def _termination(self):
    if self.data.get(self.invoke).get('termination'):
      return self.data.get(self.invoke).get('termination')
    if self.data.get('default'):
      return self.data.get('default').get('termination')
    return env.TERMINATION

  def env(self, name):
    if getattr(self, '_' + name):
      return getattr(self, '_' + name)()
    return None

  def session(self, label):
    if self.data.get(label).get('session'):
      return self.data.get(label).get('session')
    return None

# data has to be yaml format
def from_file(filepath, invoke):
  with open(filepath, 'r') as f:
    data = yaml.load(f.read())
  return Playbook(data, invoke)

# data has to be yaml format
def from_data(data, invoke):
  return Playbook(yaml.load(data), invoke)

__all__ = [from_file, from_data]
