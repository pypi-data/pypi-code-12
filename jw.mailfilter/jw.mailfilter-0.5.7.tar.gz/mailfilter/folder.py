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
Account
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from functools import partial
from pprint import pprint
from future import standard_library
from jw.util.python3hell import Bytes2Str, Bytes
from jw.util.retry import retry

from .logging2 import DEBUG2

standard_library.install_aliases()
from itertools import takewhile, chain
import email

from builtins import str
from builtins import object
import gevent
from . import filters
from . import imap

import logging
from jw.util.extension import LoadClass
import ssl
from .util import Flatten, D, DecodeHeader

#: Default IDLE timeout
IDLE_TIMEOUT = 180

class UndefinedFilter(RuntimeError):
    def __init__(self, error):
        RuntimeError.__init__(self, 'Undefined filter type: ' + error)

class Folder(object):

    def __init__(self, name, folders, config, globalConfig=None):
        """

        :param name: Mail filter name from config
        :type name: str
        :param config: config
        :type config: dict
        """
        assert isinstance(folders, list), 'folders must be a list'
        # Parameters
        self.name = name
        self.config = config
        self.globalConfig = globalConfig or {}
        self.timeout = config.get('time-out', globalConfig.get('time-out'))
        # Logging
        self.log = logging.getLogger('{}.{}'.format(str(self.__module__), self.__class__.__name__))
        # Miscellaneous setup
        self.imap = None
        self.seen = {}
        if not self._startImap():
            raise RuntimeError('Account %s not startable' % (self.name))
        # Setup folders and filters
        self.folders = [
            (name, tuple(self._filterFromString(f) for f in Flatten(filters))) for name, filters in folders
        ]
        for folder, filter in self.folders:
            self.seen[folder] = set()
            if any(f.needsBody for f in filter):
                # Full body required
                self.fetchPart = self.messagePart = 'RFC822'
            else:
                # Only headers required
                self.fetchPart = 'BODY.PEEK[HEADER]'
                self.messagePart = 'BODY[HEADER]'
        # Log
        self.log.info(
            'Account %s, folders %s: %s (%s)',
            self.name,
            ', '.join(str(f) for f in self.folders),
            self.config['address'],
            ('No SSL', 'SSL')[self.config.get('ssl', False)]
        )

    def run(self):
        """
        Mail filter

        """
        self.separator = self.imap('namespace')[0][0][1]
        idleOk = 'IDLE' in self.imap('capabilities')
        idleUsed = self.config.get('idle', idleOk)
        if idleUsed and idleUsed != idleOk:
            raise RuntimeError('Server does not support IDLE: ' + self.name)
        self._check()
        if idleUsed:
            self.imap('idle')
        while True:
            if idleUsed:
                idleResult = self.imap('idle_check', self.timeout)
                if idleResult and idleResult[1]:
                    self.log.debug('%s: %s', self.name, idleResult)
                    if idleUsed:
                        self.imap('idle_done')
                    self._check()
                    if idleUsed:
                        self.imap('idle')
            else:
                gevent.sleep(self.timeout or IDLE_TIMEOUT)
                self._check()
        self.log.critical('%s stopped', self.name)
        self.imap = None

    def _check(self, search='ALL'):
        """
        Check messages
        """
        try:
            # Check all folders in account
            for folder, filters in self.folders:
                self.log.debug('Checking folder %s in %s', folder, self.name)
                # Try to select folder
                try:
                    self.imap('select_folder', folder.replace('/', self.separator))
                except:
                    self.log.exception('From self.imap.select_folder("%s"): %s', folder)
                    continue
                # Determine messages to scan
                idlist = set(self.imap('search', search))
                seen = self.seen[folder]
                todo = idlist - seen
                self.log.log(DEBUG2, 'Seen: %s', seen)
                self.log.debug('To do: %s', todo)
                if not todo:
                    continue
                mlist = self.imap('fetch', todo, self.fetchPart)
                # Scan messages
                for m, msg in list(mlist.items()):
                    self.log.debug('Checking message %s', m)
                    # Get message from IMAP
                    try:
                        message = email.message_from_string(Bytes2Str(msg[self.messagePart.encode('utf-8', 'replace')]))
                    except KeyError as e:
                        self.log.critical('%s part not found in message %s:\n%s', self.messagePart, repr(msg)[:256], e)
                        continue
                    subject = DecodeHeader(message['Subject'])
                    # Do checks until one of them returns 'stop'
                    # [Calls to filter.check() also trigger the actions]
                    checks = list(
                        takewhile(
                            lambda item: item[1] != 'stop',
                            ((filter.filterDef['filter'], filter.check(m, self, message)) for filter in filters)
                        )
                    )
                    result = all(c[1] for c in checks)
                    self.log.info('%s %s(%s): "%s" %s %s', m, self.name, folder, subject, ('positive', 'negative')[result], checks)
                    # Add processed message
                    seen.add(m)
                self.imap('expunge')
        except:
            self.log.exception('Uncaught exception')

    def _startImap(self):
        # If connection exists, shut it down
        if self.imap is not None:
            try:
                self.imap.shutdown()
            except Exception as e:
                self.log.critical('From self.imap.shutdown() in %s: %s', self.name, e)
        # Set up SSL context
        context = ssl.create_default_context()
        context.check_hostname = False  # TODO: make configurable
        context.verify_mode = ssl.CERT_NONE  # TODO: make configurable
        # Create connection
        self.imap = retry(
            imap.IMAP,
            self.config['address'],
            self.config['username'],
            self.config['password'],
            ssl=self.config.get('ssl', False),
            ssl_context=context,
            logFailure_=partial(self.log.critical, 'imap.IMAP(%s): %s', self.name)
        )
        self.log.debug('Capabilites: %s', self.imap.capabilities())
        # Try to do STARTTLS
        if self.config.get('starttls', False):
            self.log.info('STARTTLS')
            try:
                self.imap._command_and_check('STARTTLS')
            except:
                self.log.exception('From STARTTLS command:')
        return True

    def _filterFromString(self, filterDef):
        """
        Create a Filter object from a definition

        :param filterDef:
        :type filterDef: dict
        :return: filter object
        :rtype: filters.Filter
        :raise filter.FilterError: if filter name is undefined
        """
        try:
            filterClass = LoadClass('jw.mailfilter.filter', filterDef['filter'], type_=filters.Filter)
        except KeyError:
            raise UndefinedFilter(str(filterDef))
        except Exception as e:
            raise filters.FilterError('Account definition error %s: %s' % (repr(e), repr(filterDef)))
        return filterClass(self.imap, filterDef, self.globalConfig)
