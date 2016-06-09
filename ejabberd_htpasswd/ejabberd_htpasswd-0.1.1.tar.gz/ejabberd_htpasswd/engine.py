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

import sys
import struct
import logging
import time
import re

from . import htpasswd

#------------------------------------------------------------------------------

log = logging.getLogger(__name__)

#------------------------------------------------------------------------------
class Engine(object):

  #----------------------------------------------------------------------------
  def __init__(self, options, *args, **kw):
    super(Engine, self).__init__(*args, **kw)
    self.options   = options
    self.htpasswd  = htpasswd.Htpasswd(options.htpasswd)
    self.domainsed = None
    if options.domainsed:
      # TODO: this is not "rigorous"...
      src, dst, rem = options.domainsed.split(options.domainsed[0], 3)[1:]
      # todo: use `rem`
      # todo: is there a package to help me with this?...
      self.domainsed = (re.compile(src), dst)

  #----------------------------------------------------------------------------
  def run(self):
    try:
      self._run()
    except Exception as err:
      log.exception('failed during main loop')
      raise

  #----------------------------------------------------------------------------
  def _run(self):
    log.info('beginning main processing loop')
    while True:
      request = self.read()
      log.debug(
        'request: "%s[...]" (%d bytes total)', request[0:5], len(request))
      result  = self.processRequest(request)
      log.debug('response: %r', result)
      self.write(result)

  #----------------------------------------------------------------------------
  def processRequest(self, request):
    result  = 0
    params  = request.split(':')
    cmd     = params[0]
    if cmd == 'auth':
      user, domain, cred = params[1:4]
      if domain and self.domainsed:
        domain = self.domainsed[0].sub(self.domainsed[1], domain)
      if domain:
        user = user + '@' + domain
      log.debug('authenticating %r', user)
      if not self.htpasswd.check(user, cred):
        log.warning('authentication for %r failed (bad username/password)', user)
        time.sleep(4)
        return 0
      log.info('authentication for %r succeeded', user)
      return 1

    if cmd == 'isuser':
      pass

    log.error('unknown command: %r', request)
    return 0

  #----------------------------------------------------------------------------
  def read(self):
    input_length = sys.stdin.read(2)
    (size,) = struct.unpack('>h', input_length)
    return sys.stdin.read(size)

  #----------------------------------------------------------------------------
  def write(self, result):
    token = struct.pack('>hh', 2, result)
    sys.stdout.write(token)
    sys.stdout.flush()


#------------------------------------------------------------------------------
# end of $Id$
# $ChangeLog$
#------------------------------------------------------------------------------
