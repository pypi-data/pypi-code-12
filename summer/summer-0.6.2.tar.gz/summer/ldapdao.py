# -*- coding: utf-8 -*-
# Time-stamp: < ldapdao.py (2016-02-14 09:48) >

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

"""Provides LDAP *DAO* support.  Analogy to :py:mod:`summer.dao` module.

Base :py:class:`LdapDao` provides access to virtual important attributes:

#. :py:attr:`LdapDao.session` attribute referencing
   :py:class:`ldap3.Connection`

#.  :py:attr:`LdapDao.base` attribute referencing
    :py:class:`:LdapSessionFactory.base` dn value (useful for creating LDAP
    queries)

"""

import logging

import ldap3

from .lsf import LdapSessionFactory

logger = logging.getLogger(__name__)


class LdapDao(object):

    """Base *DAO* class.  Analogy to :py:class:`summer.dao.Dao` class.

    Provides safe access to thread bound session/connection through
    :py:attr:`session` attribute and base LDAP dn value through
    :py:attr:`base` attribute.  Alternative is :py:meth:`get_session`
    and :py:meth:`get_base` respectively.

    """

    def __init__(self, ldap_session_factory: LdapSessionFactory):
        """Creates :py:class:`LdapDao` instance.

        Args:

            ldap_session_factory (LdapSessionFactory): ldap session factory
                                                       to use

        """
        self.ldap_session_factory = ldap_session_factory

    def __getattribute__(self, attrname: str) -> object:
        if attrname == "session":
            attrval = self.get_session()
            logger.debug("dao support accesses session %s", attrval)
        elif attrname == "base":
            attrval = self.get_base()
            logger.debug("dao support accesses base %s", attrval)
        else:
            attrval = object.__getattribute__(self, attrname)
        return attrval

    def get_session(self) -> ldap3.Connection:
        return self.ldap_session_factory.get_ldap_session()

    def get_base(self) -> str:
        return self.ldap_session_factory.get_session().base

class LdapEntityDao(LdapDao):

    """Base *DAO* class for persistent classes subclassed from
    :py:class:`summer.domain.LdapEntity`."""

    def __init__(self, ldap_session_factory: LdapSessionFactory, clazz: type):
        """Creates :py:class:`EntityLdapDao`.

        Args:

            ldap_session_factory (LdapSessionFactory): ldap session factory
                                                       to use

            clazz (type): reference to class type
        """
        LdapDao.__init__(self, ldap_session_factory)
        self.clazz = clazz
