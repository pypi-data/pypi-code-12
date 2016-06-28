#!/usr/bin/env python

import clip, logging, logtool, pkg_resources, subprocess
from cfgtool.cmdbase import CmdBase

LOG = logging.getLogger (__name__)

class Action (CmdBase):

  @logtool.log_call
  def __init__ (self, kwargs):
    super (Action, self).__init__ (kwargs, module_not_present = True)

  @logtool.log_call
  def run (self):
    if not self.conf.force:
      self.error ("  Must force installs (--force).")
      clip.exit (err = True)
    try:
      fpath = pkg_resources.resource_filename (self.kwargs.module,
                                               "_cfgtool/")
      fname = pkg_resources.resource_filename (self.kwargs.module,
                                               "_cfgtool/install")
    except OSError as e:
      self.error ("Module %s does not have a cfgtool install."
                  % self.kwargs.module)
      clip.exit (err = True)
    try:
      self.debug ("  Running: %s" % fname)
      subprocess.check_call ([fname,],
                             cwd = fpath,
                             shell = True,
                             universal_newlines = True)
    except subprocess.CalledProcessError as e:
      self.error ("  Error running installer: %d" % e.returncode)
      clip.exit (err = True)
