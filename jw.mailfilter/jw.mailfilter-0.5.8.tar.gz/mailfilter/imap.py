# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Wrapper for IMAPClient class
"""

from __future__ import absolute_import, print_function, unicode_literals
from __future__ import division

import imaplib

import re

from .logging2 import *

standard_library.install_aliases()
from builtins import *
from time import sleep, time
from jw.util.types import Args2Str
from imapclient import IMAPClient

import logging

IMAP_RETRIES = 10

class IMAP(IMAPClient):
    """
    IMAP access
    """

    RETRIABLE_EXCEPTIONS = (
        (IMAPClient.AbortError, None),
        (IMAPClient.Error, re.compile(r'command UID illegal in state AUTH, only allowed in states SELECTED')),
    )

    def __init__(
            self, host, username, password, *args, **kwargs
    ):
        self.username = username
        self.password = password
        self.log = logging.getLogger('{}.{}'.format(str(self.__module__), self.__class__.__name__))
        super().__init__(host, *args, **kwargs)
        self.login(username, password)

    def __call__(self, name, *args, **kwargs):
        stime = 1
        t1 = time()
        for i in range(IMAP_RETRIES):
            try:
                result = getattr(self, name)(*args, **kwargs)
                self.log.log(DEBUG2, 'IMAP: %s(%s) -> %s', name, Args2Str(args, kwargs), result)
                break
            except Exception as e:
                # Catch exceptions defined in RETRIABLE_EXCEPTIONS, reraise all others
                if not any(
                    isinstance(e, etypes) and etext.match(str(e)) if etext else True
                    for etypes, etext in self.RETRIABLE_EXCEPTIONS
                ):
                    raise
                self.log.warning(
                    'From %s(%s) in %s: %s. Next try in %d sec.', name, Args2Str(*args, **kwargs), self.host, e, stime
                )
                sleep(stime)
                stime *= 2
                try:
                    self.shutdown()
                except Exception as e2:
                    self.log.warning('From self.shutdown() in %s: %s', self.host, e2)
                try:
                    self._imap = self._create_IMAP4()
                except Exception as e2:
                    self.log.warning('From self._create_IMAP4() in %s: %s', self.host, e2)
                    self._imap = None
                    continue
                try:
                    self.login(self.username, self.password)
                except Exception as e2:
                    self.log.warning('From login("%s", "***") in %s: %s', self.username, self.host, e2)
                    continue
        else:
            self.log.critical(
                '%s(%s) in %s: Error after %s tries. Giving up.', name, Args2Str(*args, **kwargs), self.host, i + 1
            )
            raise RuntimeError('%s operation failed after %s tries' % (name, i + 1))
        if i:
            t2 = time()
            self.log.warning(
                '%s(%s) in %s: Successful after %s tries in %.1f sec.',
                name,
                Args2Str(*args, **kwargs),
                self.host,
                i,
                t2 - t1
            )
        return result
