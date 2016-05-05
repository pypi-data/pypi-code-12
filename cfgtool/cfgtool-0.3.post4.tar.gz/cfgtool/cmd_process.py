#!/usr/bin/env python

import clip, logging, logtool, temporary
from path import Path
from cfgtool.cmdbase import CmdBase

LOG = logging.getLogger (__name__)

class Action (CmdBase):

  @logtool.log_call
  def run (self):
    if not self.conf.force:
      self.error ("  Must force writes (--force).")
      clip.exit (err = True)
    rc = False
    content = None
    in_file = Path (self.kwargs.in_file)
    if not in_file.isfile ():
      self.error ("Template file does not exist.")
      clip.exit (err = True)
    self.info ("  Generate...")
    if self.kwargs.out_file == "=":
      f = Path (self.kwargs.in_file)
      out_file = f.parent / f.namebase
      rc = self.process_one_file (in_file, out_file, self.make_file)
      content = out_file.bytes ()
    elif self.kwargs.out_file:
      out_file = Path (self.kwargs.out_file)
      rc = self.process_one_file (in_file, out_file, self.make_file)
      content = out_file.bytes ()
    else:
      with temporary.temp_file () as fname:
        out_file = Path (fname)
        rc = self.process_one_file (in_file, out_file, self.make_file)
        content = out_file.bytes ()
    if not self.kwargs.out_file:
      self.info ("Produced file:")
      self.report (content)
    clip.exit (err = (True if rc else False))
