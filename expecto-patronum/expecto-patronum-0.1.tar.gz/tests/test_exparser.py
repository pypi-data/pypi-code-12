# encoding: UTF-8

import os, re, sys
import json, yaml, textwrap, traceback
import unittest
from exparser import *
from tests.comfortable import *


class TestExParser(unittest.TestCase, Comfortable):

  temp = '/tmp/ZocqVm0H'

  def setUp(self):
    self.mktemp(self.temp)

  def tearDown(self):
    self.rmtemp(self.temp)

  def strip(self, x):
    return re.sub(r'[\s+]', '', x)

  def each(self, testcase):
    sys.stdout.write("%s|%s ... " % (__name__, os.path.basename(testcase)))
    (playbook, expect) = self.prepare(testcase)
    try:
      actual = self.to_json(ExParser(playbook).parse())
      # no exception raised
      # can't find difference unless using strip...
      test = self.strip(actual) == self.strip(expect)
      if not test: self.info(actual, expect)
      sys.stdout.write("%s\n" % ('ok' if test else 'ng'))
      assert test
    except:
      exc_type, exc_value, _ = sys.exc_info()
      actual = "%s %s" % (str(exc_type), exc_value)
      test = len(re.findall(expect, actual, re.DOTALL)) > 0
      sys.stdout.write("%s\n" % ('ok' if test else 'ng'))
      if not test: print(traceback.format_exc())
      assert test

  def test_all(self):
    sys.stdout.write("\n")
    for testcase in self.get_testcases("parser"):
      self.each(testcase)
