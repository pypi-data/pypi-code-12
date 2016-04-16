# -*- coding: utf-8 -*-
# Time-stamp: < lx.py (2016-02-14 10:00) >

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

"""Module ``lx`` contains support for programmatic ldap session/connection
management.  Analogy to :py:mod:`summer.tx` module.

Declarative ldap session management is defined in :py:mod:`summer.lxaop`.

"""

import logging

from .ex import AbstractMethodException
from .lsf import LdapSessionFactory

logger = logging.getLogger(__name__)


class LdapCallback(object):

    """Callback object called from within a :py:class:`LdapWrapper`.  Analogy
    to :py:class:`summer.tx.TransactionCallback` class."""

    def lxrun(self, session: LdapSessionFactory.Local, *args, **kwargs):
        """Executed inside ldap session/connection.

        This is a callback method.  It is discouraged to use the ``*args``
        and ``**kwargs`` magic.

        Args:

            session (LdapSessionFactory.Local): *ldap3* session/connection

        Returns:

            object: whatever you want to get returned

        """
        raise AbstractMethodException()


class LdapWrapper(object):

    """Wraps the code it executes inside a LDAP session/connection.  Analogy to
    :py:class:`summer.tx.TransactionWrapper` class.

    Caller provides a callback object (:py:class:`LdapCallback` instance)
    to be executed inside a session/connection; it gets passed in the
    current thread-bound :py:class:`LdapSessionFactory.Local` instance
    (which can access *ldap3* session).

    It participates in current session/connection if there is one active or
    creates a new one.

    """

    def __init__(self, ldap_session_factory: LdapSessionFactory):
        self.ldap_session_factory = ldap_session_factory

    def execute(self, callback: LdapCallback, *args, **kwargs):
        """Runs the callback provided (a ``LdapCallback`` instance) in a new ldap session.

        Whatever other arguments are provided, they are passed to callback.

        Args:

            callback (LdapCallback): callback to be executed

        Returns:

            object: whatever the callback returns
        """
        session = self.ldap_session_factory.get_session()
        logger.debug("lx begin with session %s", session)
        active = session.active
        try:
            if active:
                logger.debug("lx active, continue")
            else:
                session.bind()
                logger.debug("lx not active, bounded")
            result = callback.lxrun(session, *args, **kwargs)
            logger.debug("lx ok")
        except Exception as ex:
            logger.exception("lx error")
            raise ex
        finally:
            if active:
                logger.debug("lx active, not closing")
            else:
                # TODO martin.slouf -- analogy to tx.py -- close or not to close?
                # session.unbound()
                # logger.debug("lx session unbounded")
                pass
        return result
