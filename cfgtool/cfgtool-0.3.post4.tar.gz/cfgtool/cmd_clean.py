#!/usr/bin/env python

import logging, logtool
from cfgtool.cmdbase import CmdBase

LOG = logging.getLogger (__name__)

class Action (CmdBase):

  @logtool.log_call
  def run (self):
    self.report ("  Clean...")
    for fname in self.cfgfiles:
      for ext in [self.conf.backup_ext, self.conf.check_ext,
                  self.conf.sample_ext]:
        for f in fname.dirname ().glob ("%s%s*" % (fname.basename (), ext)):
          self.report ("    Removing: %s" % f)
          f.remove ()
