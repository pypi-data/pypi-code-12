# -*- coding: utf-8 -*-
# Time-stamp: < txaop.py (2016-02-14 12:26) >

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

"""Declarative transaction management."""

import logging
import types

from sqlalchemy.orm import Session

from .aop import AroundMethodAdvice, Proxy
from .tx import TransactionCallback, TransactionWrapper
from .sf import SessionFactory

logger = logging.getLogger(__name__)


def transactional(func: types.FunctionType):
    """Method decorator marking method as transactional.

    Use together with :py:class:`TransactionAdvice` and
    :py:class:`TransactionalProxy`.

    Methods decorated with :py:func:`transactional` can be run within a
    transaction if wrapped in :py:class:`TransactionalProxy`.

    Usually it is required to access *SQLAlchemy* session from within the
    transaction.  Encouraged access to current thread-bound *SQLAlchemy*
    session is through :py:class:`summer.sf.SessionFactory`.

    Preferred way to manipulate your persistent entities is through *DAO*
    objects (:py:mod:`summer.dao`).  Intended use case for this decorator
    is to mark such :py:class:`summer.dao.EntityDao` methods and then
    access current *SQLAlchemy* session by using
    :py:attr:`summer.dao.Dao.session` from within the *DAO* method.  Thus
    you can access *SQLAlchemy* session (and manipulate data), and still
    have the transaction boundaries defined on top of your business
    methods.

    Args:

        func (types.FunctionType): function to be decorated

    """
    func.transactional = True
    # mame .. method name
    # mame = "%s.%s" % (func.im_class.__name__, func.__name__)
    mame = func.__name__
    logger.debug("method %s decorated as transactional", mame)
    return func


class TransactionAdvice(AroundMethodAdvice):

    """Together with :py:func:`transactional` decorator forms a *transaction
    aspect*.  Advice gets invoked if method is marked with
    :py:func:`transactional` and if object is wrapped in
    :py:class:`TransactionProxy`.

    """

    class Callback(TransactionCallback):

        def __init__(self, advice):
            """Creates internal :py:class:`TransactionCallback` instance.

            Args:

                advice (TransactionAdvice): reference to parent
                                            :py:class:`TransactionAdvice`

            """
            TransactionCallback.__init__(self)
            self.advice = advice

        def txrun(self, session: Session, *args, **kwargs):
            result = self.advice.method(*args, **kwargs)
            return result

    def __init__(self, method: types.MethodType,
                 session_factory: SessionFactory):
        """Creates :py:class:`TransactionAdvice` instance.

        Args:

            method (types.MethodType): instance method marked by
                                       :py:func:`transactional` decorator

            session_factory (SessionFactory): session factory to be used

        """
        AroundMethodAdvice.__init__(self, method)
        self.session_factory = session_factory

    def around(self, *args, **kwargs):
        """Wraps the target method invocation within a transaction.  If any
        exception is raised it gets re-thrown and the transaction is rolled
        back, see :py:class:`summer.tx.TransactionWrapper`.

        """
        logger.debug("tx around advice start for '%s'", self.mame)
        tx = TransactionWrapper(self.session_factory)
        callback = TransactionAdvice.Callback(self)
        try:
            result = tx.execute(callback, *args, **kwargs)
            logger.debug("tx around advice end for '%s'", self.mame)
            return result
        except Exception as ex:
            logger.exception("tx around advice error for '%s'", self.mame)
            raise ex


class TransactionProxy(Proxy):

    """Intercepts method invocations on target object with transaction logic.

    It either calls the target object's method directly or invokes the
    :py:class:`TransactionAdvice` if the method is marked by
    :py:func:`transactional`.

    """

    def __init__(self, target: object, session_factory: SessionFactory=None):
        """Creates the :py:class:`TransactionProxy` instance.

        Searches the *target* object for :py:func:`transactional` decorated
        methods.  It creates a :py:class:`TransactionalAdvice` object for
        each method found.  Invocation of such a method means invoking a
        :py:class:`TransactionalAdvice` object instead, wrapping the call
        with transaction.

        Args:

            target (object): any object that is searched for transactional
                             methods


            session_factory (SessionFactory): session factory to be used;
                                              if ``None``, *target* object
                                              is searched for
                                              ``session_factory`` attribute
                                              which is used instead

        """
        Proxy.__init__(self, target)
        logger.info("creating tx proxy for '%s'", target)
        if session_factory is None:
            self.session_factory = target.session_factory
        else:
            self.session_factory = session_factory
        methods = self._get_decorated_methods(transactional.__name__)
        for i in methods:
            advice = TransactionAdvice(i, self.session_factory)
            setattr(self, i.__name__, advice)
            logger.debug("tx advice '%s' created", advice)
