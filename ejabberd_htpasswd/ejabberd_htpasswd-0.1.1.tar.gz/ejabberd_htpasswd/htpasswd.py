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

import bcrypt
import logging

# TODO: cache the htpasswd file... **BUT** only do that if there is
#       also a check for if the file changes

#------------------------------------------------------------------------------

log = logging.getLogger(__name__)

#------------------------------------------------------------------------------
class Htpasswd(object):

  #----------------------------------------------------------------------------
  def __init__(self, filename, *args, **kw):
    super(Htpasswd, self).__init__(*args, **kw)
    self.filename = filename

  #----------------------------------------------------------------------------
  def _getEntries(self):
    with open(self.filename, 'rb') as fp:
      data = fp.read().strip().split('\n')
      data = [item.split(':', 1)
              for item in data
              if item and not item.startswith('##')]
      return dict(data)

  #----------------------------------------------------------------------------
  def isUser(self, username):
    return username in self._getEntries()

  #----------------------------------------------------------------------------
  def check(self, username, credential):
    check = self._getEntries().get(username, None)
    if check is None:
      log.warning('check for unknown user %r', username)
      return False
    if check.startswith('$2a$') or check.startswith('$2y$'):
      return check == bcrypt.hashpw(credential, check)
    log.error('unknown htpasswd hash entry for user %r', username)
    return False


#------------------------------------------------------------------------------
# end of $Id$
# $ChangeLog$
#------------------------------------------------------------------------------
