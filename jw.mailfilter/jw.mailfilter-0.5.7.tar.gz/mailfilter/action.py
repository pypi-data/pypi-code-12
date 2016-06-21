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
Actions
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division

from functools import partial

from future import standard_library
from gevent import spawn
from jw.util.python3hell import Bytes2Str
from jw.util.retry import retry

standard_library.install_aliases()
from builtins import *
from email.mime.message import MIMEMessage
import imaplib
from itertools import chain
from smtplib import SMTPException, SMTP_SSL, SMTP
from email.mime.multipart import MIMEMultipart
import time
from urllib.request import urlopen

import pyzor

from pyzor.digest import DataDigester

from .util import FromRe
import logging
from .logging2 import *

Logger = logging.getLogger(__name__)

class Action(object):
    def __init__(self, imap, config, globalConfig):
        """
        Create Action object

        :param imap: IMAP client
        :type imap: imapclient.IMAPClient
        :param config_:
        :type config: dict

        Needs to be called from derived classes
        """
        self.imap = imap
        self.config = config
        self.globalConfig = globalConfig
        self._needsBody = False

    def run(self, msgid, folder, message):
        """
        Run filter

        :param int msgid: message ID
        :param str message: mail message

        To be derived in subclass
        """

    @property
    def needsBody(self):
        return self._needsBody

class CopyToAction(Action):
    """
    Action: copy to folder
    """
    def __init__(self, imap, config, globalConfig):
        """

        :param imap: IMAP client
        :type imap: imapclient.IMAPClient
        :param config:
        :type config: dict
        """
        self.folder = config[0]
        self.log = logging.getLogger('{}.{}'.format(str(self.__module__), self.__class__.__name__))
        super(CopyToAction, self).__init__(imap, config, globalConfig)

    def copy(self, msgid, separator='/'):
        """
        Copy message to another folder

        :param msgid: message ID
        :type msgid: int
        """
        # Make namespace-prefixed folder name (for Courier servers)
        personal = self.imap('namespace').personal[0]
        parent = personal[0].strip(personal[1])
        if parent:
            parent += personal[1]
        folder = parent + self.folder.replace('/', separator)
        # Copy message
        for _ in range(2):
            try:
                self.imap.copy(msgid, folder)
                break
            except imaplib.IMAP4.error:
                # On IMAP error assume destination folder does not exist. Create it.
                try:
                    self.imap.create_folder(folder)
                except Exception as e:
                    self.log.critical('Could not create folder: %s', e)
                else:
                    self.log.info('%s: Created folder %s', self.imap.host, folder)
            except Exception as e:
                self.log.critical('Unrecoverable error from imap.copy(): %s', e)
                return False
        else:
            self.log.critical('Failed to copy message %s', msgid)
            return False
        return True

    def run(self, msgid, folder, message):
        """
        Run action

        :param msgid: Message ID
        :type msgid: int
        :param message: Message object
        :type message: email.email
        """
        if self.copy(msgid, folder.separator):
            self.log.info('Message %d copied to folder %s', msgid, self.folder)

class MoveToAction(CopyToAction):
    def __init__(self, imap, config, globalConfig):
        """
        Create MoveToAction object

        :param imap: IMAP client
        :type imap: imapclient.IMAPClient
        :param config:
        :type config: dict
        """
        super(MoveToAction, self).__init__(imap, config, globalConfig)

    def run(self, msgid, folder, message):
        """

        :param msgid:
        :param message:
        """
        if self.copy(msgid, folder.separator):
            self.imap.delete_messages(msgid)
            self.imap.expunge()
            self.log.info('Message %d moved to folder %s', msgid, self.folder)
        else:
            self.log.critical('Copy failed, could not move message %s', msgid)

class DeleteAction(Action):
    """
    Action: delete message
    """

    def __init__(self, imap, config, globalConfig):
        """
        Create DeleteAction object

        :param imap: IMAP client
        :type imap: imapclient.IMAPClient
        :param config:
        :type config: dict
        """
        self.log = logging.getLogger('{}.{}'.format(str(self.__module__), self.__class__.__name__))
        super(DeleteAction, self).__init__(imap, config, globalConfig)

    def run(self, msgid, folder, message):
        """

        :param msgid:
        :param message:
        """
        self.imap.delete_messages(msgid)
        self.imap.expunge()
        self.log.info('Message %d deleted', msgid)

class SetFlagAction(Action):
    """
    Action: set a flag
    """

    def __init__(self, imap, config, globalConfig):
        """
        Create SetFlagAction object

        :param imap: IMAP client
        :type imap: imapclient.IMAPClient
        :param config:
        :type config: dict
        """
        self.log = logging.getLogger('{}.{}'.format(str(self.__module__), self.__class__.__name__))
        self.flags = config
        super(SetFlagAction, self).__init__(imap, config, globalConfig)

    def run(self, msgid, folder, message):
        """

        :param msgid:
        :param message:
        """
        self.imap.set_flags(msgid, self.flags)
        self.log.info('Message %d flag(s) %s set', msgid, self.flags)

class ClearFlagAction(Action):
    """
    Action: clear a flag
    """

    def __init__(self, imap, config, globalConfig):
        """
        Create DeleteAction object

        :param imap: IMAP client
        :type imap: imapclient.IMAPClient
        :param config:
        :type config: dict
        """
        self.log = logging.getLogger('{}.{}'.format(str(self.__module__), self.__class__.__name__))
        self.flags = config
        super(ClearFlagAction, self).__init__(imap, config, globalConfig)

    def run(self, msgid, folder, message_):
        """

        :param msgid:
        :param message_:
        """
        self.imap.remove_flags(msgid, self.flags)
        self.log.info('Message %d flag(s) %s cleared', msgid, self.flags)

class PyzorReportAction(Action):
    """
    Action: report spam to Pyzor
    """

    def __init__(self, imap, config, globalConfig):
        """
        Create a PyzorReport object
        """
        self.log = logging.getLogger('{}.{}'.format(str(self.__module__), self.__class__.__name__))
        self.pyzorClient = pyzor.client.Client()
        super(PyzorReportAction, self).__init__(imap, config, globalConfig)

    @property
    def needsBody(self):
        return True

    def run(self, msgid, folder, message):
        """

        :param msgid:
        :param message:
        """
        digest = DataDigester(message)
        try:
            hexdigest = digest.digest.hexdigest()
            self.pyzorClient.report(hexdigest)
        except Exception as e:
            self.log.critical('From self.pyzorClient.report("%s"):', hexdigest, e)
        else:
            self.log.info('Reported %s to pyzor (digest %s)', msgid, hexdigest)

class ForwardAction(Action):
    """
    Action: forward mail
    """

    def __init__(self, imap, config, globalConfig):
        """
        Create a ForwardAction object
        """
        self.log = logging.getLogger('{}.{}'.format(str(self.__module__), self.__class__.__name__))
        super(ForwardAction, self).__init__(imap, config, globalConfig)

    def run(self, msgid, folder, message):
        """

        :param int msgid:
        :param str message:
        """
        fmessage = MIMEMultipart()
        smtp = folder.config.get('smtp', self.globalConfig['smtp'])
        username = smtp.get('username', folder.config['username'])
        password = smtp.get('password', folder.config['password'])
        fmessage['From'] = smtp.get('from', username)
        fmessage['To'] = self.config[0]
        fmessage['Date'] = time.ctime()
        fmessage['Subject'] = 'Fwd: %s' % Bytes2Str(message['subject'])
        fmessage.attach(MIMEMessage(message))
        spawn(retry, self.send, fmessage, msgid, password, smtp, username)

    def send(self, fmessage, msgid, password, smtp, username):
        try:
            self.log.debug('Forwarding message %s', msgid)
            try:
                session = SMTP(smtp['host'])
                session.starttls()
                self.log.log(DEBUG2, 'STARTTLS connection to %s established', smtp['host'])
            except SMTPException as e:
                session = SMTP_SSL(smtp['host'])
                self.log.log(DEBUG2, 'SSL connection to %s established', smtp['host'])
            session.login(username, password)
            session.sendmail(fmessage['from'], self.config[0], fmessage.as_string())
            session.quit()
            self.log.info('Message %s forwarded to %s', msgid, self.config[0])
        except Exception:
            self.log.exception('Uncaught exception in %s.send()', self.__class__.__name__)

class StopAction(Action):
    """
    Action: stop action sequence
    """

    def __init__(self, imap, config, globalConfig):
        """
        Create StopAction object

        :param imap: IMAP client
        :type imap: imapclient.IMAPClient
        :param config:
        :type config: dict
        """
        self.log = logging.getLogger('{}.{}'.format(str(self.__module__), self.__class__.__name__))
        super(StopAction, self).__init__(imap, config, globalConfig)

    def run(self, msgid, folder, message):
        """

        :param msgid:
        :param message:
        """
        self.log.info('%s: Stop', msgid)
        return 'stop'

class ReportBadipsAction(Action):
    """
    Action: report to badips.com
    """

    def __init__(self, imap, config, globalConfig):
        """
        Create ReportBadipsAction object

        :param imap: IMAP client
        :type imap: imapclient.IMAPClient
        :param config:
        :type config: dict
        """
        self.log = logging.getLogger('{}.{}'.format(str(self.__module__), self.__class__.__name__))
        super(ReportBadipsAction, self).__init__(imap, config, globalConfig)

    def run(self, msgid, folder, message):
        """

        :param msgid:
        :param message:
        """
        received = message.get_all('received')
        if received:
            try:
                mta = next(
                    # First non-empty element of tuple
                    t[0] or t[1]
                        # Tuples with one of the elements containing an IP
                        for t in chain.from_iterable(FromRe.findall(i) for i in received if i.startswith('from '))
                )
            except StopIteration:
                self.log.warning('No "Received: from" header in message %s', msgid)
                return
            try:
                url = 'https://www.badips.com/add/%s/%s' % ('badbots', mta)
                self.log.log(DEBUG2, 'HTTP GET %s', url)
                self.log.info("%s: Reported %s -> %s", msgid, mta, urlopen(url).read())
            except Exception as e:
                self.log.critical('%s: Reporting spammer %s as "badbots": %s', msgid, mta, e)
        else:
            self.log.warning('No Received header in message %s', msgid)
