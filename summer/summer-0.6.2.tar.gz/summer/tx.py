# -*- coding: utf-8 -*-
# Time-stamp: < tx.py (2016-02-14 01:05) >

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

"""Module ``tx`` contains support for programmatic transaction management.

Declarative transaction management is defined in :py:mod:`summer.txaop`.

"""

import logging

from sqlalchemy.orm import Session

from .ex import AbstractMethodException
from .sf import SessionFactory

logger = logging.getLogger(__name__)


class TransactionCallback(object):

    """Callback object called from within a :py:class:`TransactionWrapper`."""

    def txrun(self, session: Session, *args, **kwargs) -> object:
        """Executed inside transaction.

        This is a callback method.  It is discouraged to use the ``*args`` and
        ``**kwargs`` magic.

        Args:

            session (Session): *SQLAlchemy* session

        Returns:

            object: whatever you want to get returned from a transaction

        """
        raise AbstractMethodException()


class TransactionWrapper(object):

    """Wraps the code it executes inside a transaction.

    Caller provides a callback object (:py:class:`TransactionCallback`
    instance) to be executed inside a transaction; it gets passed in the
    current thread-bound *SQLAlchemy* session.

    It participates in current transaction if there is one active or
    creates a new one.

    If exception is raised, transaction is rolled back.

    """

    def __init__(self, session_factory: SessionFactory):
        """
        Args:

            session_factory (SessionFactory): session factory to be used
        """
        self.session_factory = session_factory

    def execute(self, callback: TransactionCallback, *args, **kwargs) -> object:
        """Runs the callback provided inside transaction.

        Whatever other arguments are provided, they are passed to callback.

        Args:

            callback (TransactionCallback): callback to be executed

        Returns:

            object: whatever the callback returns
        """
        session = self.session_factory.get_session()
        logger.debug("tx begin with session %s", session)
        active = session.active
        try:
            if active:
                logger.debug("tx active, continue")
            else:
                session.begin()
                logger.debug("tx not active, started")
            sqlalchemy_session = session.sqlalchemy_session
            result = callback.txrun(sqlalchemy_session, *args, **kwargs)
            if active:
                logger.debug("tx active, no commit")
            else:
                sqlalchemy_session.commit()
                logger.debug("tx commit")
        except Exception as ex:
            session.rollback()
            logger.exception("tx rollback")
            raise ex
        finally:
            if active:
                logger.debug("tx active, not closing")
            else:
                # TODO martin.slouf -- decide whether session can outlive
                # the transaction -- can be handy and less resourceful
                # session.close()
                # logger.debug("tx closed")
                pass
        return result
