# -*- coding: utf-8 -*-
# Time-stamp: < lsf.py (2016-02-14 10:53) >

# Copyright (C) 2009-2016 Martin Slouf <martin.slouf@sourceforge.net>
#
# This file is a part of Summer.
#
# Summer is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

"""Module ``lsf`` defines :py:class:`LdapSessionFactory` class which is
central point for your *LDAP database* access.

Ananalogy to :py:mod:`summer.sf`.

"""

import ldap3
import logging
import threading

logger = logging.getLogger(__name__)


class LdapSessionFactory(object):

    """Thread safe *ldap3* session provider.  Analogy to
    :py:class:`summer.sf.SessionFactory`.

    """

    class Local(threading.local):

        """Thread local session wrapper.

        There is an active :py:class:`ldap3.Connection` instance in
        :py:attr:`ldap_session` attribute.

        """

        def __init__(self, base: str):
            threading.local.__init__(self)
            self.base = base
            self.ldap_session = None
            self.active = False

        def __del__(self):
            self.unbind()

        def bind(self):
            if self.ldap_session:
                self.ldap_session.bind()
                self.active = True

        def unbind(self):
            if self.ldap_session:
                self.ldap_session.unbind()
                self.ldap_session = None
                self.active = False
                # FIXME martin.slouf -- logger may not be accessible as module may be destroyed before object
                # logger.debug("thread-local ldap session unbound")

    def __init__(self, hostname: str, port: int, base: str, login: str,
                 passwd: str):
        """Creates :py:class:`LdapSessionFactory` instance.

        Args:

            hostname (str): server hostname

            port (int): server port

            base (str): LDAP base dn

            login (str): server login

            passwd (str): server password in clear text
        """
        self.hostname = hostname
        self.port = port
        self.base = base
        self.login = login
        self.passwd = passwd
        self.session = LdapSessionFactory.Local(self.base)

        # define an unsecure LDAP server, requesting info on DSE and schema
        self.server = ldap3.Server(hostname, port, get_info=ldap3.ALL)

    def get_session(self):
        """Get current thread-local *ldap3 session* wrapper (creating one, if non-existent).

        Returns:

            LdapSessionFactory.Local: existing or just created *ldap3
                                      session* wrapper

        """
        ldap_session = self.session.ldap_session
        if ldap_session:
                logger.debug("accessing session = %s", ldap_session)
        else:
            ldap_session = ldap3.Connection(
                self.server,
                client_strategy=ldap3.STRATEGY_SYNC,
                user=self.login,
                password=self.passwd,
                authentication=ldap3.AUTH_SIMPLE,
                check_names=True)
            logger.debug("new thread local session created, session = %s",
                         ldap_session)
            self.session.ldap_session = ldap_session
        return self.session

    def get_ldap_session(self) -> ldap3.Connection:
        """Get current *ldap3* session.

        See :py:meth:`get_session` method.

        Returns:

            ldap3.Connection: existing of just created *ldap3* session.
        """
        return self.get_session().ldap_session
