# -*- coding: utf-8 -*-
# Time-stamp: < lxaop.py (2016-02-14 10:52) >

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

"""Declarative LDAP session/connection management.  Analogy to
:py:mod:`summer.txaop` module.

"""

import logging
import types

from .aop import AroundMethodAdvice, Proxy
from .lsf import LdapSessionFactory
from .lx import LdapCallback, LdapWrapper

logger = logging.getLogger(__name__)


def ldapaop(func: types.FunctionType):
    """Method decorator marking method as transactional.  Analogy to
    :py:func:`summer.txaop.transactional`.

    Use together with :py:class:`LdapAdvice` and :py:class:`LdapProxy`.

    Methods decorated with :py:func:`ldapaop` can be run within a LDAP
    session/connection if wrapped in :py:class:`LdapProxy`.

    Intended use case for this decorator is to decorate
    :py:class:`summer.ldapdao.LdapEntityDao` methods and then access
    current *ldap3* session/connection by using
    :py:attr:`summer.ldapdao.LdapDao.session` from within the *DAO* method.
    Thus you can access *ldap3* session/connection (and manipulate data),
    and still have the transaction boundaries defined on top of your
    business methods.

    Args:

        func (types.FunctionType): function to be decorated

    """
    func.ldapaop = True
    # mame .. method name
    # mame = "%s.%s" % (func.im_class.__name__, func.__name__)
    mame = func.__name__
    logger.debug("method %s decorated as ldapaop", mame)
    return func


class LdapAdvice(AroundMethodAdvice):

    """Together with :py:func:`transactional` decorator forms a *transaction
    aspect*.  Analogy to :py:class:`summer.txaop.TransactionAdvice`.

    Advice gets invoked if method is marked with :py:func:`ldapaop` and if
    object is wrapped in :py:class:`LdapProxy`.

    """

    class Callback(LdapCallback):

        def __init__(self, advice):
            """Creates internal :py:class:`LdapCallback` instance.

            Args:

                advice (LdapAdvice): reference to parent
                                     :py:class:`TransactionAdvice`

            """
            self.advice = advice

        def lxrun(self, session: LdapSessionFactory.Local, *args, **kwargs):
            result = self.advice.method(*args, **kwargs)
            return result

    def __init__(self, method: types.MethodType,
                 ldap_session_factory: LdapSessionFactory):
        """Creates :py:class:`LdapAdvice` instance.

        Args:

            method (types.MethodType): instance method marked by
                                       :py:func:`ldapaop` decorator

            ldap_session_factory (LdapSessionFactory): ldap session factory
                                                       to be used

        """

        AroundMethodAdvice.__init__(self, method)
        self.ldap_session_factory = ldap_session_factory

    def around(self, *args, **kwargs):
        """Wraps the target method invocation within a ldap session/connection.  If
        any exception is raised it gets re-thrown, see
        :py:class:`summer.lx.LdapWrapper`.

        """
        lx = LdapWrapper(self.ldap_session_factory)
        callback = LdapAdvice.Callback(self)
        try:
            logger.debug("lx advice start for '%s'", self.mame)
            result = lx.execute(callback, *args, **kwargs)
            logger.debug("lx advice end for '%s'", self.mame)
            return result
        except Exception as ex:
            logger.exception("lx advice error for '%s'", self.mame)
            raise ex


class LdapProxy(Proxy):

    """Intercepts method invocations on target object with ldap
    session/connection logic.

    It either calls the target object's method directly or invokes the
    :py:class:`LdapAdvice` if the method is marked by
    :py:func:`ldapaop`.

    """

    def __init__(self, target: object,
                 ldap_session_factory: LdapSessionFactory=None):
        """Creates the :py:class:`LdapProxy` instance.

        Searches the *target* object for :py:func:`ldapaop` decorated
        methods.  It creates a :py:class:`LdapAdvice` object for each
        method found.  Invocation of such a method means invoking a
        :py:class:`LdapAdvice` object instead, wrapping the call with ldap
        session/connection.

        Args:

            target (object): any object that is searched for ldap
                             methods


            ldap_session_factory (LdapSessionFactory): ldap session factory
                                                       to be used; if
                                                       ``None``, *target*
                                                       object is searched
                                                       for
                                                       ``ldap_session_factory``
                                                       attribute which is
                                                       used instead

        """
        Proxy.__init__(self, target)
        logger.info("creating ldap proxy for '%s'", target)
        if ldap_session_factory is None:
            self.ldap_session_factory = target.ldap_session_factory
        else:
            self.ldap_session_factory = ldap_session_factory
        methods = self._get_decorated_methods(ldapaop.__name__)
        for i in methods:
            advice = LdapAdvice(i, self.ldap_session_factory)
            setattr(self, i.__name__, advice)
            logger.debug("ldap advice '%s' created", advice)
