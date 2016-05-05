#!/usr/bin/env python

import logging, logtool
from cfgtool.cmdbase import CmdBase

LOG = logging.getLogger (__name__)

class Action (CmdBase):

  @logtool.log_call
  def run (self):
    rc = self.process_cfgs ("Generate...",
                            self.conf.templ_ext, self.conf.check_ext,
                            self.make_file)
    if not rc:
      rc = self.process_cfgs ("Check...",
                              "", self.conf.check_ext,
                              self.compare_files)
    return rc
