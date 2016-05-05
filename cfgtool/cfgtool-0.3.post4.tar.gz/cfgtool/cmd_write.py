#!/usr/bin/env python

import clip, logging, logtool
from cfgtool.cmdbase import CmdBase

LOG = logging.getLogger (__name__)

class Action (CmdBase):

  @logtool.log_call
  def run (self):
    if not self.conf.force:
      self.error ("  Must force writes (--force).")
      clip.exit (err = True)
    rc = self.process_cfgs ("Generate...",
                            self.conf.templ_ext, "",
                            self.make_file)
    clip.exit (err = (True if rc else False))
