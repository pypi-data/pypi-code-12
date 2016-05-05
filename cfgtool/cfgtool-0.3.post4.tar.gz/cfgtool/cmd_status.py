#!/usr/bin/env python

import clip, logging, logtool
from cfgtool.cmdbase import CmdBase

LOG = logging.getLogger (__name__)

class Action (CmdBase):

  @logtool.log_call
  def run (self):
    for module in self.cfgs:
      rc = Action (module).run ()
    clip.exit (err = (True if rc else False))
