#!/usr/bin/env python

import clip, json, logging, logtool, numbers
from six import string_types
from cfgtool.cmdbase import CmdBase

LOG = logging.getLogger (__name__)

class Action (CmdBase):

  @logtool.log_call
  def run (self):
    value = (self.belief if not self.kwargs.belief
             else self.get_belief (self.kwargs.belief))
    if not value:
      self.error ("Belief not found: %s" % self.kwargs.belief)
      clip.exit (err = True)
    elif isinstance (value, numbers.Number) or isinstance (value, string_types):
      self.report (value)
    else:
      self.report (json.dumps (value, indent = 2))
    return 0
