#!/usr/bin/env python

from __future__ import print_function
import clip, logging, logging.config, logtool, os, sys
from functools import partial
from addict import Dict
from path import Path
from configobj import ConfigObj
from cfgtool import __version__

logging.basicConfig (level = logging.WARN)
LOG = logging.getLogger (__name__)

APP = clip.App ()
PROCESS_UTTIME, PROCESS_STRTIME = logtool.now (slug = True)
DEFAULT_CONFIGFILE = "etc/cfgtool/cfgtool.conf"
DEFAULT_BELIEFDIR = "etc/cfgtool/belief.d"
DEFAULT_MODULEDIR = "etc/cfgtool/module.d"
DEFAULT_WORKDIR = "/"
CONFIG = Dict ({
  "nobackup": False,
  "debug": False,
  "templ_ext": ".templ",
  "belief_ext": ".json",
  "backup_ext": "-backup",
  "check_ext": "-check",
  "notroot": False,
  "only": False,
  "out_ext": "",
  "sample_ext": ".sample",
  "time_ut": PROCESS_UTTIME,
  "time_str": PROCESS_STRTIME,
})

class CmdError (Exception):
  pass

@logtool.log_call
def option_setopt (option, value):
  CONFIG[option] = value

@logtool.log_call
def option_version (opt): # pylint: disable = W0613
  print (__version__)
  clip.exit ()

@logtool.log_call
def option_logging (flag):
  logging.root.setLevel (logging.DEBUG)
  CONFIG.debug = flag

@APP.main (name = Path (sys.argv[0]).basename (),
           description = "cfgtool",
           tree_view = "-H")
@clip.flag ('-H', '--HELP', hidden = True, help = "Show all sub-commands")
@clip.flag ("-b", "--nobackup",
            help = "Disable backups of touched files",
            default = False, hidden = True, inherit_only = True,
            callback = partial (option_setopt, "nobackup"))
@clip.opt ("-B", "--beliefdir",
           help = "Belief directory to use.",
           default = DEFAULT_WORKDIR + DEFAULT_BELIEFDIR, hidden = True,
           inherit_only = True,
           callback = partial (option_setopt, "belief_dir"))
@clip.flag ("-C", "--nocolour",
            help = "Suppress colours in reports",
            default = False, hidden = True, inherit_only = True,
            callback = partial (option_setopt, "nocolour"))
@clip.flag ("-D", "--debug",
            help = "Enable debug logging",
            default = False, hidden = True, inherit_only = True,
            callback = option_logging)
@clip.flag ("-f", "--force", help = "Don't stop at errors",
            default = False, hidden = True, inherit_only = True,
            callback = partial (option_setopt, "force"))
@clip.opt ("-M", "--moduledir",
           help = "Module directory to use.",
           default = DEFAULT_WORKDIR + DEFAULT_MODULEDIR, hidden = True,
           inherit_only = True,
           callback = partial (option_setopt, "module_dir"))
@clip.flag ("-N", "--notroot",
            help = "Allow running as non-root",
            default = False, hidden = True, inherit_only = True,
            callback = partial (option_setopt, "notroot"))
@clip.flag ("-O", "--only_data",
            help = "Suppress information output",
            default = False, hidden = True, inherit_only = True,
            callback = partial (option_setopt, "only"))
@clip.opt ("-W", "--workdir",
           help = "Working root directory to use.",
           default = DEFAULT_WORKDIR, hidden = True, inherit_only = True,
           callback = partial (option_setopt, "work_dir"))
@clip.flag ("-q", "--quiet",
            help = "Suppress output",
            default = False, hidden = True, inherit_only = True,
            callback = partial (option_setopt, "quiet"))
@clip.flag ("-v", "--verbose",
            help = "Verbose output (see variable mappings)",
            default = False, hidden = True, inherit_only = True,
            callback = partial (option_setopt, "verbose"))
@clip.flag ("-V", "--Version",
            help = "Report installed version",
            default = False, hidden = True, inherit_only = True,
            callback = option_version)
@logtool.log_call
def app_main (*args, **kwargs): # pylint: disable = W0613
  if not CONFIG.notroot and os.geteuid () != 0:
    # Here so that help is available to non-root
    LOG.error ("%s must be run as root (or use --notroot)",
               Path (sys.argv[0]).basename ())
    sys.exit (1)
  if not sys.stdout.isatty ():
    option_setopt ("nocolour", True)
  CONFIG.work_dir = Path (CONFIG.get ("work_dir", DEFAULT_WORKDIR))
  CONFIG.module_dir = Path (CONFIG.get ("module_dir",
                                        CONFIG.work_dir / DEFAULT_MODULEDIR))
  CONFIG.belief_dir = Path (CONFIG.get ("belief_dir",
                                        CONFIG.work_dir / DEFAULT_BELIEFDIR))

@logtool.log_call
def main ():
  try:
    cfg = ConfigObj (DEFAULT_WORKDIR + DEFAULT_CONFIGFILE,
                     interpolation = False)
    CONFIG.update (dict (cfg))
  except: # pylint: disable = W0702
    print ("Unable to parse config file: %s" % DEFAULT_CONFIGFILE,
           file = sys.stderr)
    sys.exit (9)
  try:
    APP.run ()
  except clip.ClipExit as e:
    sys.exit (1 if e.status else 0)
  except (CmdError, KeyboardInterrupt):
    sys.exit (2)
  except Exception as e:
    logtool.log_fault (e)
    sys.exit (3)

if __name__ == "__main__":
  main ()
