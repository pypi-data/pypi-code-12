# encoding: UTF-8

import sys, pexpect, env
from exparser import *


class StackTrace(object):

  def __init__(self):
    self.stacks = []

  def push(self, statement, message):
    if isinstance(statement, Statement):
      self.stacks.append({
        "statement": statement,
        "message": message
      })

  def head(self):
    if len(self.stacks) > 0:
      return self.stacks[1]
    return None

  def last(self):
    if len(self.stacks) > 0:
      return self.stacks[-1]
    return None

  def report(self):
    return "\n".join([x.get('message') for x in self.stacks]).strip()


class Context(object):

  def __init__(self, timeout, stdout):
    self.timeout = timeout
    self.stdout = stdout
    self.__vars = {}

  def setvar(self, k, v):
    self.__vars[k] = v

  def getvar(self, k):
    return self.__vars[k]


class Interpreter(object):

  def __init__(self, playbook):
    self.playbook = playbook
    self.stacktrace = StackTrace()
    timeout, stdout = self.playbook.env('timeout'), self.playbook.env('stdout')
    self.context = Context(timeout = timeout, stdout = stdout)

  # close spawned process if not killed
  def __terminate(self, subprocess, label):
    # terminate if socket is opened
    if self.stacktrace.last().get('statement').is_termination():
      return
    # terminate with interact if default interact setting is settle
    # TODO: I think that it have to move reference of playbook object to somewhere
    if Type.Interact == self.playbook.env('termination'):
      statement = InteractStatement()
      statement.interpret(
        subprocess = subprocess,
        context = self.context,
        stacktrace = self.stacktrace
      )
      return
    # terminate with exit
    statement = TerminateStatement()
    statement.interpret(
      subprocess = subprocess,
      context = self.context,
      stacktrace = self.stacktrace
    )

  def report(self):
    return self.stacktrace.report()

  # session should end with one of the 3 reply, either 'interact', 'terminate' or 'exit'.
  def interpret(self):
    stacks = ExParser(self.playbook).parse()
    if len(stacks) == 0:
      return
    # start
    subprocess = stacks[0].interpret(context = self.context, stacktrace = self.stacktrace)
    for statement in stacks[1:]:
      # check whether sub process is already spawned.
      # aborted calling spawn twice is under restriction.
      if statement.type == Type.Spawn:
        break
      else:
        statement.interpret(
          subprocess = subprocess,
          context = self.context,
          stacktrace = self.stacktrace
        )
      if self.stacktrace.last().get('statement').is_termination():
        return
    self.__terminate(subprocess, self.playbook.invoke)
