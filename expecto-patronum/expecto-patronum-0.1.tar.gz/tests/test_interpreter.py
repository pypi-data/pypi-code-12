# encoding: UTF-8

import os, re, sys
import json, yaml, textwrap, traceback
import unittest
from tests.comfortable import *
from interpreter import *

class TestInterpreter(unittest.TestCase, Comfortable):

  temp = '/tmp/ZocqVm0H'

  def setUp(self):
    self.mktemp(self.temp)

  def tearDown(self):
    self.rmtemp(self.temp)

  def each(self, testcase):
    sys.stdout.write("%s|%s ... " % (__name__, os.path.basename(testcase)))
    (playbook, expect) = self.prepare(testcase)
    try:
      env.STDOUT = False
      interpret = Interpreter(playbook)
      interpret.interpret()
      actual = interpret.report()
      # no exception raised
      test = expect == actual
      if not test: self.info(actual, expect)
      sys.stdout.write("%s\n" % ('ok' if test else 'ng'))
      assert test
    except:
      exc_type, exc_value, _ = sys.exc_info()
      actual = "%s %s" % (str(exc_type), exc_value)
      test = re.findall(expect, actual, re.DOTALL)
      sys.stdout.write("%s\n" % ('ok' if test else 'ng'))
      if not test: print(traceback.format_exc())
      assert test

  def test_all(self):
    sys.stdout.write("\n")
    for testcase in self.get_testcases("interpreter"):
      self.each(testcase)
