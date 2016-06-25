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
The filter module provides various filters for sorting out spam
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from future import standard_library

from .util import FromRe, DecodeHeader

standard_library.install_aliases()
from socket import gaierror
from itertools import chain
import logging
import re
import shlex
from urllib.parse import urlparse
import bs4
from gevent.socket import gethostbyname
import pyzor.client
from pyzor.digest import DataDigester
from jw.util.memoize import memoizeFor
from jw.util.extension import LoadClass, ResourceNotFound
from jw.util.split import Splitter

from . import action
from . import content
from .logging2 import *

SPAM_URL_CACHE_TIME = 3600
SPLIT_RE = re.compile(r'"[^"]*(?:"|$)|\S+')

Log = logging.getLogger(__name__)

@memoizeFor(SPAM_URL_CACHE_TIME)
def CheckSpamUrl(url):
    """
    Check a URL whether it's spamvertised

    :param url: URL
    :type url: str
    :return: True if spamvertised
    :rtype : bool
    """
    parts = url.split('.')
    for i in range(2, 4):
        if len(parts) >= i:
            cpart = '.'.join(parts[-i:])
            if cpart:
                try:
                    ip = gethostbyname(cpart + '.multi.surbl.org')
                    Log.info('URL %s positive', cpart)
                    if ip.startswith('127.'):
                        return True
                    else:
                        Log.warning('Weird result from multi.surbl.org: %s', ip)
                except gaierror:
                    Log.debug('URL %s ok', cpart)
                except Exception as e:
                    Log.critical('gethostbyname of %s (%s) yielded %s', repr(cpart), repr(parts), e)
    return False

def GetPayload(part):
    payload = part.get_payload(decode=True)
    if payload is None:
        payload = ''
    else:
        if isinstance(payload, bytes):
            payload = payload.decode(part.get_content_charset('latin1'), errors='replace')
        elif not isinstance(payload, str):
            Log.error('Payload %s is %s', repr(payload)[:256])
            payload = ''
    return payload

class SpamActionError(RuntimeError):
    """
    Error on spam action parsing
    """

class FilterError(RuntimeError):
    """
    Error parsing filter arguments
    """

class Filter(object):
    """
    Filter base

    """
    def __init__(self, imap, filterDef, globalConfig):
        """
        Create Filter object

        :param imap: IMAP client
        :type imap: imapclient.IMAPClient
        :param filterDef:
        :type filterDef: dict
        :raise SpamActionError:

        Needs to be called from derived classes
        """
        # General setup
        self._needsBody = False
        # Copy parameters
        self.imap = imap
        self.filterDef = filterDef
        self.globalConfig = globalConfig
        # Setup action
        self.spamAction = []
        actions = filterDef['action']
        if not isinstance(actions, list):
            actions = actions,
        for a in actions:
            lexer = shlex.shlex(a, posix=True)
            lexer.whitespace_split = True
            spam = list(lexer)
            try:
                actionClass = LoadClass('jw.mailfilter.action', spam[0], type_=action.Action)
                action_ = actionClass(imap, spam[1:], self.globalConfig)
                self.spamAction.append(action_)
                self._needsBody = self._needsBody or action_.needsBody
            except ResourceNotFound:
                raise SpamActionError('Undefined spam action %s in %s' % (spam[0], filterDef))

    def check(self, id, folder, message):
        """
        Run filter

        :param id:
        :type id: int
        :param message:
        :type message: email.email
        :return: True if good, False if bad
        :rtype: bool
        """
        raise NotImplementedError('check')

    def spam(self, id, folder, message):
        """
        Run spam action

        :param id:
        :type id: int
        :param message:
        :type message: email.message
        """
        for a in self.spamAction:
            a.run(id, folder, message)

    @property
    def needsBody(self):
        """
        Get body requirements

        :return: True if filter needs examination of BODY
        :rtype: bool
        """
        return self._needsBody

    @staticmethod
    def extract(message):
        """
        Extract payload

        :param message:
        :type message:
        :return: body
        :rtype: unicode
        """
        if message.is_multipart():
            return ''.join(BodyFilter.extract(m) for m in message.get_payload(decode=True))
        else:
            return message.get_payload(decode=True) or message.get_payload(decode=True)

class All(Filter):
    def __init__(self, imap, filterDef, globalConfig):
        self.log = logging.getLogger('{}.{}'.format(str(self.__module__), self.__class__.__name__))
        super().__init__(imap, filterDef, globalConfig)

    def check(self, msgid, folder, message):
        """
        Run filter

        :param msgid:
        :param message:
        :return: False
        :rtype: bool

        Returns False for all mail
        """
        self.spam(msgid, folder, message)
        return False

class RblFilter(Filter):
    """
    RBL filter
    """
    def __init__(self, imap, filterDef, globalConfig):
        error = False
        try:
            self.rbl = filterDef['org']
            regex = filterDef.get('positiv')
            self.re = re.compile(regex) if regex else None
        except:
            error = True
        if error:
            raise FilterError(
                'rbl filter syntax is: {filter: rbl, org: domain, [positiv: regex], spam: action}, got "%s"' % repr(filterDef)
            )
        self.log = logging.getLogger('{}.{}'.format(str(self.__module__), self.__class__.__name__))
        super().__init__(imap, filterDef, globalConfig)

    def check(self, msgid, folder, message):
        """
        Run filter

        :param msgid:
        :type msgid: int
        :param message:
        :type message: email.email
        :return: True if ok
        :rtype: bool
        """
        received = message.get_all('received')
        if received:
            ipv4list = list(chain.from_iterable(FromRe.findall(i) for i in received if i.startswith('from ')))
            if not ipv4list:
                ipv6list = list(
                    chain.from_iterable(
                        re.findall(r'[\[(](\d+\.\d+\.\d+\.\d+)[\])]', i) for i in message.get_all('received')
                    )
                )
                self.log.warning('No Received-headers with usable IPs in message')
                return False
            else:
                ip = ipv4list[0][1]
                revip = '.'.join(reversed(ip.split('.')))
                dname = '{}.{}'.format(revip, self.rbl)
                try:
                    result = gethostbyname(dname)
                except:
                    # Not spam
                    pass
                else:
                    # Prevent positive (spam) result only if a result regex is not matched
                    if self.re and self.re.match(result) is None:
                        return True
                    self.spam(msgid, folder, message)
                    self.log.info('Message %d from spammer IP %s', msgid, ip)
                    return False
        return True

class ContentFilter(Filter):
    """
    Content filter
    """

    def __init__(self, imap, filterDef, globalConfig):
        """
        Create ContentFilter object

        :param imap: IMAP client
        :type imap: imapclient.IMAPClient
        :param filterDef: filter definition
        :type filterDef: dict
        """
        self.log = logging.getLogger('{}.{}'.format(str(self.__module__), self.__class__.__name__))
        # Setup check
        args = Splitter(filterDef['check']).split()
        if args[0] not in content.FILTER_FUNCTIONS:
            raise FilterError('No such content check: ' + filterDef['check'])
        else:
            self.filterFunction = content.FILTER_FUNCTIONS[args[0]](filterDef, args[1:])
        super().__init__(imap, filterDef, globalConfig)

    @property
    def needsBody(self):
        """
        Get body requirements

        :return: True if filter needs mail BODY
        :rtype: bool
        """
        return True

class BodyFilter(ContentFilter):
    """
    Content filter

    .. seealso:: Filter
    """
    def __init__(self, imap, filterDef, globalConfig):
        """
        Create ContentFilter object

        :param imap: IMAP client
        :type imap: imapclient.IMAPClient
        :param filterDef: filter definition
        :type filterDef: dict
        """
        self.filter = filterDef
        self.log = logging.getLogger('{}.{}'.format(str(self.__module__), self.__class__.__name__))
        super().__init__(imap, filterDef, globalConfig)

    def check(self, msgid, folder, message):
        """
        Run filter

        :param msgid:
        :type msgid: int
        :param message:
        :type message: email.email
        :return: True if ok
        :rtype: bool
        """
        result = self.filterFunction.check(msgid, self.extract(message))
        if result:
            self.log.info('Body of message %d positive', msgid)
            self.spam(msgid, folder, message)
        return not result

class HeaderFilter(ContentFilter):
    """
    Header filter

    .. seealso:: Filter
    """
    def __init__(self, imap, filterDef, globalConfig):
        """
        Create ContentFilter object

        :param imap: IMAP client
        :type imap: imapclient.IMAPClient
        :param filterDef: filter definition
        :type filterDef: dict
        """
        self.filter = filterDef
        self.header = filterDef['part'].lower()
        self.log = logging.getLogger('{}.{}'.format(str(self.__module__), self.__class__.__name__))
        super().__init__(imap, filterDef, globalConfig)

    def check(self, msgid, folder, message):
        """
        Run filter

        :param msgid:
        :type msgid: int
        :param message:
        :type message: email.email
        :return: True if ok
        :rtype: bool
        """
        field = DecodeHeader(message[self.header])
        result = self.filterFunction.check(msgid, field)
        self.log.debug('result: %s [%s]', result, field)
        if result:
            self.spam(msgid, folder, message)
        return not result

class PyzorFilter(Filter):
    """
    Filter with pyzor
    """

    def __init__(self, imap, filterDef, globalConfig):
        """
        Create a PyzorFilter object
        """
        self.filter = filterDef
        self.log = logging.getLogger('{}.{}'.format(str(self.__module__), self.__class__.__name__))
        self.pyzorClient = pyzor.client.Client()
        super().__init__(imap, filterDef, globalConfig)

    def check(self, msgid, folder, message):
        """
        Run filter

        :param msgid:
        :type msgid: int
        :param message:
        :type message: email.email
        :return: True if ok
        :rtype: bool
        """
        digest = DataDigester(message)
        presult = self.pyzorClient.check(digest.digest.hexdigest())
        if presult['Diag'] != 'OK':
            self.log.warning('Pyzor: %s ==> %s', str(presult).replace('\n', ' '))
        result = int(presult['Count']) == 0
        if not result:
            self.spam(msgid, folder, message)
        return result

    @property
    def needsBody(self):
        """
        Get body requirements

        :return: True if filter needs mail BODY
        :rtype: bool
        """
        return True

class BayesFilter(ContentFilter):
    """
    Bayes filter
    """

    def __init__(self, imap, filterDef, globalConfig):
        """
        Create a BayesFilter object
        """
        self.log = logging.getLogger('{}.{}'.format(str(self.__module__), self.__class__.__name__))
        super().__init__(imap, filterDef, globalConfig)

    def check(self, msgid, folder, message):
        return False

class UrlFilter(Filter):
    """
    URL content filter
    """

    def __init__(self, imap, filterDef, globalConfig):
        """
        Create a UrlFilter object
        """
        self.log = logging.getLogger('{}.{}'.format(str(self.__module__), self.__class__.__name__))
        super().__init__(imap, filterDef, globalConfig)

    def check(self, msgid, folder, message):
        """
        Run filter

        :param msgid:
        :type msgid: int
        :param message:
        :type message: email.email
        :return: True if ok
        :rtype: bool
        """
        # Check all parts
        if message.is_multipart():
            result = any(self.checkPart(m) for m in message.get_payload())
        else:
            result = self.checkPart(message)
        if result:
            self.spam(msgid, folder, message)
        return not result

    def checkPart(self, part):
        """
        Check part of e-mail for spam URLs

        :param part: payload
        :type part: email.message.Message
        :return: True if a spam URL was found
        :rtype: bool

        HTML has tags with href checked on top of text
        """
        payload = GetPayload(part)
        if part.get_content_type() == 'text/html':
            # First check href in tags
            soup = bs4.BeautifulSoup(payload, 'html.parser')
            for e in soup.findAll(href=True):
                parsed = urlparse(e['href'])
                if parsed.scheme:
                    url = parsed.netloc
                else:
                    url = parsed.path
                if CheckSpamUrl(url):
                    return True
            return False
        elif part.get_content_type() == 'text/plain':
            text = payload
            urls = set(m.group(1) for m in re.finditer(r'https?://([^/ \t\r\n">?,;:[\]{}!]+)', text))
            self.log.log(DEBUG2, 'URLs found: %s', urls)
            return any(CheckSpamUrl(u) for u in urls)
