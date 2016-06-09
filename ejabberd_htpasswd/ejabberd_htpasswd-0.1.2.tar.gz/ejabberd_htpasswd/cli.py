# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: metagriffin <mg.github@metagriffin.net>
# date: 2016/06/09
# copy: (C) Copyright 2016-EOT metagriffin -- see LICENSE.txt
#------------------------------------------------------------------------------
# This software is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
#------------------------------------------------------------------------------

import logging
import logging.handlers
import argparse
import time

from .i18n import _
from . import engine

#------------------------------------------------------------------------------

DEFAULT_HTPASSWD        = '/var/www/.htpasswd'
DEFAULT_LOGFILE         = '/var/log/ejabberd/auth-htpasswd.log'
DEFAULT_LOGSIZE         = 1048576
DEFAULT_LOGCOUNT        = 10

#------------------------------------------------------------------------------
def main(argv=None):

  cli = argparse.ArgumentParser(
    description = _(
      'Yet another ejabberd authentication bridge that uses apache-style'
      ' .htpasswd files.'),
  )

  cli.add_argument(
    _('-d'), _('--debug'),
    dest='debug', action='store_true', default=False,
    help=_('enable debugging output'))

  cli.add_argument(
    _('-l'), _('--log-file'), metavar=_('FILENAME'),
    dest='logfile', action='store', default=DEFAULT_LOGFILE,
    help=_('specify the logging file; default: "%(default)s"'))

  cli.add_argument(
    _('-s'), _('--log-size'), metavar=_('BYTES'),
    dest='logsize', action='store', type=int, default=DEFAULT_LOGSIZE,
    help=_('specify the maximum size of the logging file;'
           ' default: %(default)s'))

  cli.add_argument(
    _('-c'), _('--log-count'), metavar=_('NUMBER'),
    dest='logcount', action='store', type=int, default=DEFAULT_LOGCOUNT,
    help=_('specify the maximum number of logging rotation files;'
           ' default: %(default)s'))

  cli.add_argument(
    _('-t'), _('--domain-transform'), metavar=_('EXPR'),
    dest='domainsed', action='store', default=None,
    help=_('specify a "sed" substitution expression for domain name'
           ' transformation; example:'
           ' "-t /chat\\.example\\.com/example\\.com/"'))

  cli.add_argument(
    'htpasswd', metavar=_('FILENAME'),
    nargs='?', default=DEFAULT_HTPASSWD,
    help=_('path to apache-style ".htpasswd" file; default: "%(default)s"'))

  options = cli.parse_args(args=argv)

  # todo: i should really do this:
  #         logging.config.fileConfig(options.logconfig)
  #       ...

  logging.basicConfig()

  root = logging.getLogger()
  for handler in root.handlers:
    root.removeHandler(handler)
  handler = logging.handlers.RotatingFileHandler(
    options.logfile,
    maxBytes    = options.logsize,
    backupCount = options.logcount,
  )
  handler.setFormatter(logging.Formatter(
    fmt       = '[%(asctime)s] %(levelname)-5.5s [%(name)s,pid=%(process)d] %(message)s',
    datefmt   = '%Y-%m-%dT%H:%M:%SZ',
  ))
  handler.formatter.converter = time.gmtime
  root.addHandler(handler)
  root.setLevel(logging.DEBUG if options.debug else logging.INFO)

  try:
    proc = engine.Engine(options)
  except Exception:
    root.exception('failed starting ejabberd-htpasswd engine')
  proc.run()

#------------------------------------------------------------------------------
# end of $Id$
# $ChangeLog$
#------------------------------------------------------------------------------
