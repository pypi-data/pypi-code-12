# encoding: UTF-8

import os, sys, re, pexpect, env

try:
  from compiler.ast import flatten
except:
  # compiler.ast.flatten is deplicated in 3.x.
  # this is the alternate.
  def flatten(seq):
    l = []
    for elt in seq:
      t = type(elt)
      if t is tuple or t is list:
        for elt2 in flatten(elt):
          l.append(elt2)
      else:
        l.append(elt)
    return l


class Message(object):

  IllegalSpawn = 'Illegal spawn statement'
  IllegalSend = 'Illegal send statement'
  IllegalExpectExpression = 'Illegal expression'
  IllegalExpect = 'Illegal expect statement'
  IllegalRecursiveInclude = 'Illegal recursive include'
  UndefinedFunction = 'Undefined function'
  TimeoutExceeded = 'Timeout Exceeded'


class Type(object):

  Spawn = 'spawn'
  Send = 'send'
  SpawnOrSend = 'spawn-or-send'
  Expect = 'expect'
  Pass = 'pass'
  Include = 'include'
  Interact = 'interact'
  Terminate = 'terminate'
  Exit = 'exit'


class Statement(object):

  def __init__(self, type):
    self.type = type

  def match(self, type):
    return self.type == type

  def is_termination(self):
    return self.type in (Type.Interact, Type.Terminate, Type.Exit)

  def is_begin(self):
    return self.type in (Type.Spawn, Type.SpawnOrSend)

  # TODO: raise exception for requiring override method
  def interpret(self, subprocess, context, stacktrace = None):
    # have to be overriden
    raise Exception("%s has to be overriden" % __name__)


class SpawnStatement(Statement):

  def __init__(self, body):
    super(SpawnStatement, self).__init__(Type.Spawn)
    self.body = body.strip()

  def __set_output_if_desired(self, subprocess, context):
    if context.stdout:
      # pexpect in python3 is throwing error as “must be in str , not bytes”
      # because sys.stdout defaults to expecting strings. Internal buffer is bytes.
      if env.IF_PYTHON_VERSION_2X:
        subprocess.logfile_read = sys.stdout
      if env.IF_PYTHON_VERSION_3X:
        subprocess.logfile = sys.stdout.buffer
    return subprocess

  # TODO: fix exception comment
  def interpret(self, context, stacktrace = None):
    if type(self.body) is str:
      if stacktrace:
        stacktrace.push(self, "spawn %s" % self.body)
        subprocess = pexpect.spawn(self.body)
        self.__set_output_if_desired(subprocess, context)
      return subprocess
    raise Exception('Unexpected Type: %s in %s' % (self.body, __name__))


class SendStatement(Statement):

  def __init__(self, body):
    super(SendStatement, self).__init__(Type.Send)
    self.body = body.strip()

  # TODO: fix exception comment
  def interpret(self, subprocess, context, stacktrace = None):
    if type(self.body) is str:
      if stacktrace:
        stacktrace.push(self, "send %s" % self.body)
      subprocess.sendline(self.body)
      return
    raise Exception('Unexpected Type: %s in %s' % (self.body, __name__))


class SpawnOrSendStatement(Statement):

  def __init__(self, body):
    super(SpawnOrSendStatement, self).__init__(Type.SpawnOrSend)
    self.body = body

  # TODO: fix exception comment
  def interpret(self, subprocess = None, context = None, stacktrace = None):
    if subprocess is not None:
      SendStatement(self.body).interpret(subprocess, context, stacktrace)
      return
    return SpawnStatement(self.body).interpret(context, stacktrace)


class ExpectExpression(object):

  def __init__(self, test, consequent, var = None):
    self.test = test
    self.var = var
    self.consequent = consequent


# TODO: we should consider to implement using collection.
class ExpectStatement(Statement):

  def __init__(self):
    super(ExpectStatement, self).__init__(Type.Expect)
    self.expressions = []

  def push(self, expr):
    if type(expr) is not ExpectExpression:
      raise Exception("Instance of ExpectExpression class is expected. %s" % type(expr))
    self.expressions.append(expr)

  def pick(self, key):
    return [e.__dict__.get(key) for e in self.expressions]

  def item(self, idx, as_dict = True):
    if as_dict:
      return self.expressions[idx].__dict__
    return self.expressions[idx]

  def size(self):
    return len(self.expressions)

  def interpret(self, subprocess, context, stacktrace = None):
    # added default pattern to tail of List
    conditions = self.pick('test') + [pexpect.TIMEOUT]
    timeout = context.timeout if context.timeout else env.TIMEOUT
    idx = subprocess.expect(conditions, timeout = timeout)
    if idx < self.size():
      if stacktrace:
        stacktrace.push(self, "expect %s" % self.item(idx).get('test').strip())
      # set variable to context
      if self.item(idx).get('var') is not None:
        if subprocess.match.group():
          var, value = self.item(idx).get('var'), subprocess.match.group()
          # we have to decode string for compatibility between py2.x and py3.x
          body = "%s=%s" % (var, value.decode('utf-8'))
          SendStatement(str(body)).interpret(subprocess, context, stacktrace)
      for step in self.item(idx).get('consequent'):
        step.interpret(subprocess, context, stacktrace)
    # catch timeout exception
    if idx == self.size():
      raise Exception("Timeout exceeded. Unexpected reply.\n%s" % subprocess.buffer)
    # catch eof exception
    # if idx == self.size() + 1:
    #   pass


class PassStatement(Statement):

  def __init__(self):
    super(PassStatement, self).__init__(Type.Pass)

  def interpret(self, subprocess, context, stacktrace = None):
    # do nothing
    pass


class InteractStatement(Statement):

  def __init__(self):
    super(InteractStatement, self).__init__(Type.Interact)

  def interpret(self, subprocess, context, stacktrace = None):
    if stacktrace:
      stacktrace.push(self, "interact")
    subprocess.interact()


class TerminateStatement(Statement):

  def __init__(self):
    super(TerminateStatement, self).__init__(Type.Terminate)

  def interpret(self, subprocess, context, stacktrace = None):
    if stacktrace:
      stacktrace.push(self, "terminate")
    stdout = context.stdout if context.stdout else env.STDOUT
    # execute termination with timeout
    timeout = context.timeout if context.timeout else env.TIMEOUT
    subprocess.terminate()
    # output log
    subprocess.expect(pexpect.EOF, timeout = timeout)


class ExParser(object):

  def __init__(self, playbook):
    self.playbook = playbook
    self.scopes = []

  # parse expect statement
  #
  # e.g.
  #   - expect: baz
  #
  #   - expect:
  #     - foo: pass
  #
  def __parse_expect(self, exprs):
    expect = ExpectStatement()
    if type(exprs) is str:
      (test, var) = self.__parse_variable(exprs)
      expect.push(ExpectExpression(test, [PassStatement()], var))
      return expect
    # there is a difference of list order depending on the environment
    for expr in sorted(exprs.keys()):
      (test, var) = self.__parse_variable(expr)
      consequent = exprs.get(test)
      if type(consequent) is str:
        expect.push(ExpectExpression(test, flatten([self.__parse_each_step(consequent.strip())]), var))
      if type(consequent) is list:
        expect.push(ExpectExpression(test, flatten([self.__parse_each_step(step) for step in consequent]), var))
    return expect

  def __parse_variable(self, expr):
    if type(expr) is str:
      m = re.match(r"^\s*?(.*?\(.+\).*?)\s*?\|\>\s*\$(.+)\s*?", expr)
      if m:
        (test, var) = m.groups()
        return (test, var)
    return (expr, None)

  def __parse_func(self, step):
    # check whether input token is `include function`
    m = re.match(r"^include\((.+)\)$", step)
    if m:
      return self.__parse_program(m.groups()[0])

  def __parse_each_step(self, step):
    if Type.Spawn in step:
      return SpawnStatement(step.get(Type.Spawn))
    if Type.Send in step:
      return SendStatement(step.get(Type.Send))
    if Type.SpawnOrSend in step:
      return SpawnOrSendStatement(step.get(Type.SpawnOrSend))
    if Type.Expect in step:
      return self.__parse_expect(step.get(Type.Expect))
    if Type.Pass == step:
      return PassStatement()
    if Type.Terminate == step:
      return TerminateStatement()
    if Type.Interact == step:
      return InteractStatement()
    if Type.Exit == step:
      return TerminateStatement()
    if type(step) is str:
      return self.__parse_func(step)
    raise Exception("Unexpected Type Error: %s in ExParser.__parse_each_step" % step)

  # TODO: fix exception comment
  def __parse_program(self, label):
    # avoid recursive include
    if not label in self.scopes:
      if self.playbook.session(label):

        # role of scope is for allowing sequential include.
        #
        # session:
        #   - include(foo)
        #   - include(foo)
        #
        self.scopes.append(label)
        steps = flatten([self.__parse_each_step(step) for step in self.playbook.session(label)])
        self.scopes.pop()

        return steps
    raise Exception("Recursive Include Error: %s in ExParser.__parse_program" % label)

  # TODO: fix exception comment
  def parse(self):
    stacks = self.__parse_program(self.playbook.invoke)
    if len(stacks) > 0 and not stacks[0].is_begin():
      if self.playbook.env('spawn'):
        spawn = SpawnStatement(self.playbook.env('spawn'))
        return [spawn] + stacks
      raise Exception("Error: session have to begin with 'spawn'.")
    return stacks
