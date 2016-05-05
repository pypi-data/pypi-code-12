#! /usr/bin/env python

from __future__ import absolute_import
import clip, logging, logtool
from .main import app_main, CONFIG
from .cmdbase import implementation

LOG = logging.getLogger (__name__)
OPTIONS = ["help", "workdir", "moduledir", "beliefdir", "nobackup", "debug",
           "force", "nocolour", "quiet", "verbose", "notroot", "only_data",]

@app_main.subcommand (
  name = "belief",
  description = "Report the belief for a module(s)",
  inherits = OPTIONS)
@clip.arg ("module", required = False,
           help = "Module to report beliefs for (optional)")
@clip.arg ("belief", required = False,
           help = "Name of belief to report (optional)")
@logtool.log_call
def belief (**kwargs):
  rc = 0
  if kwargs.get ("module"):
    rc += implementation ("belief", **kwargs)
  else:
    for module in sorted ([f.basename ()
                           for f in CONFIG.module_dir.glob ("*")]):
      rc += implementation ("belief", module = module, **kwargs)
  if rc:
    clip.exit (err = True)

@app_main.subcommand (
  name = "check",
  description = "Check currency of configuration files",
  inherits = OPTIONS)
@clip.arg ("module", required = True,
           help = "Module to process")
@logtool.log_call
def check (module):
  rc = implementation ("check", module = module)
  if rc:
    clip.exit (err = True)

@app_main.subcommand (
  name = "clean",
  description = "Remove old backups",
  inherits = OPTIONS)
@clip.arg ("module", required = True,
           help = "Module to process")
@logtool.log_call
def clean (module):
  implementation ("clean", module = module)

@app_main.subcommand (
  name = "process",
  description = "Process file as part of the module",
  inherits = OPTIONS)
@clip.arg ("module", required = True,
           help = "Module to process")
@clip.arg ("in_file", required = True,
           help = "Template file to process")
@clip.arg (
  "out_file", required = False,
  help = "Output file to write (optional, '=' removes last extension)")
@logtool.log_call
def process (**kwargs):
  implementation ("process", **kwargs)

@app_main.subcommand (
  name = "pyinstall",
  description = "Install module's support files (requires --force)",
  inherits = OPTIONS)
@clip.arg ("module", required = True,
           help = "Module to process")
@logtool.log_call
def pyinstall (module):
  implementation ("pyinstall", module = module)

@app_main.subcommand (
  name = "sample",
  description = "Generate sample configuration files",
  inherits = OPTIONS)
@clip.arg ("module", required = True,
           help = "Module to process")
@logtool.log_call
def sample (module):
  implementation ("sample", module = module)

@app_main.subcommand (
  name = "status",
  description = "Report status of configuration files",
  inherits = OPTIONS)
@logtool.log_call
def status ():
  rc = 0
  for module in sorted ([f.basename ()
                         for f in CONFIG.module_dir.glob ("*")]):
    rc += implementation ("check", module = module)
  if rc:
    clip.exit (err = True)

@app_main.subcommand (
  name = "write",
  description = "Write new configuration files (requires --force)",
  inherits = OPTIONS)
@clip.arg ("module", required = True,
           help = "Module to process")
@logtool.log_call
def write (module):
  implementation ("write", module = module)
