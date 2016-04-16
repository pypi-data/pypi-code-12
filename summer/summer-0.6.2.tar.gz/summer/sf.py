# -*- coding: utf-8 -*-
# Time-stamp: < sf.py (2016-02-29 07:25) >

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

"""Module ``sf`` defines :py:class:`SessionFactory` class which is central
point for your ORM mapping and *SQL database* access.

"""

import logging
import threading

from sqlalchemy import (
    create_engine,
    MetaData,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.engine import (
    Engine,
    Connection,
)
from sqlalchemy.engine.interfaces import Dialect

from .ex import SummerConfigurationException

logger = logging.getLogger(__name__)


class SessionFactory(object):

    """Thread safe *SQLAlchemy* session provider."""

    class Local(threading.local):

        """Thread local session & connection wrapper."""

        def __init__(self, engine: Engine):
            threading.local.__init__(self)
            self.engine = engine
            self.sqlalchemy_session = None
            self.connection = None
            self.active = False  # True if transaction is active

        def __del__(self):
            self.close()

        def get_connection(self) -> Connection:
            if not self.connection:
                self.connection = self.engine.connect()
            return self.connection

        def close(self):
            if self.sqlalchemy_session:
                self.sqlalchemy_session.close()
                self.sqlalchemy_session = None
                self.active = False
                # FIXME martin.slouf -- logger may not be accessible as
                # module may be destroyed before object
                # logger.debug("thread-local db session closed")
            if self.connection:
                self.connection.close()

        def begin(self):
            if self.sqlalchemy_session and self.active:
                self.sqlalchemy_session.begin()
                self.active = True

        def commit(self):
            if self.sqlalchemy_session:
                self.sqlalchemy_session.commit()
                self.active = True

        def rollback(self):
            if self.sqlalchemy_session:
                self.sqlalchemy_session.rollback()
                self.active = True

    def __init__(self, uri: str, echo: bool, autoflush: bool, autocommit: bool, **kwargs):
        """Creates :py:class:`SessionFactory` instance.

        Args:

            uri (str): *SQLAlchemy* connection string (including username
                       and password)

            echo (bool): print out SQL commands

            autoflush (bool): whether autoflush is enabled (if unsure, set
                              to ``True``)

            autocommit (bool): whether autocommit is enabled (if unsure set
                               to ``False``)

            kwargs (dict): passed directly to *SQLAlchemy*
                           :py:class:`sessionmaker`

        """
        self.uri = uri
        self.echo = echo
        self.autoflush = autoflush
        self.autocommit = autocommit
        self.rlock = threading.RLock()
        # NOTE martin.slouf -- needs to set via 'set_table_definitions'
        self.table_definitions = None
        # NOTE martin.slouf -- needs to set via 'set_class_mappings'
        self.class_mappings = None

        self.engine = create_engine(uri, echo=echo)
        self.metadata = MetaData(bind=self.engine)
        self.sessionmaker = sessionmaker(bind=self.engine,
                                         autoflush=autoflush,
                                         autocommit=autocommit,
                                         **kwargs)
        self.session = SessionFactory.Local(self.engine)

    def set_table_definitions(self, table_definitions):
        """Sets table definitons.

        See :py:meth:`summer.context.Context.orm_init` method.

        """
        self.table_definitions = table_definitions
        self.table_definitions.define_tables(self)
        logger.info("table definitions registered: %s",
                    self.metadata.tables)

    def set_class_mappings(self, class_mappings):
        """Sets class mappings.

        See :py:meth:`summer.context.Context.orm_init` method.

        """
        if self.table_definitions is None:
            msg = "unable to register mappings -- set table definitions first"
            raise SummerConfigurationException(msg)
        self.class_mappings = class_mappings
        self.class_mappings.create_mappings(self)
        logger.info("class mappings registered")

    def create_schema(self):
        """Create database schema using *SQLAlchemy*.  Call once
        :py:attr:`table_definitions` are set.

        """
        if self.table_definitions is None:
            msg = "unable to create schema -- set table definitions first"
            raise SummerConfigurationException(msg)
        # delegate call to ORM layer
        self.metadata.drop_all()
        self.metadata.create_all()

    def get_session(self):
        """Get current thread-local *SQLAlchemy session* wrapper (creating one, if
        non-exististent).

        Returns:

            SessionFactory.Local: existing or just created *SQLAlchemy
                                  session* wrapper

        """
        sqlalchemy_session = self.session.sqlalchemy_session
        if sqlalchemy_session:
            logger.debug("accessing session = %s", self.session)
        else:
            sqlalchemy_session = self.sessionmaker()
            logger.debug("new thread local session created, session = %s",
                         self.session)
            self.session.sqlalchemy_session = sqlalchemy_session
        return self.session

    def get_sqlalchemy_session(self) -> Session:
        """Get current *SQLAlchemy* session.

        See :py:meth:`get_session` method.

        Returns:

            Session: existing of just created *SQLAlchemy* session.
        """
        return self.get_session().sqlalchemy_session

    def get_connection(self) -> Connection:
        return self.get_session().get_connection()

    def get_dialect_name(self) -> Dialect:
        return self.engine.name


class AbstractTableDefinitions(object):

    """
    Container for *SQLAlchemy* table definitions.  Registers itself at
    session factory.  A callback class -- use to provide table definitions
    to ORM.

    See :py:meth:`summer.context.Context.orm_init` method.
    """

    def define_tables(self, session_factory: SessionFactory):
        """Override in subclasses to define database tables."""
        pass


class AbstractClassMappings(object):

    """Container for *SQLAlchemy* mappings.  Registers itself at session
    factory.  A callback class -- use to provide class mappings to ORM.

    See :py:meth:`summer.context.Context.orm_init` method.

    """

    def create_mappings(self, session_factory: SessionFactory):
        """Override in subclasses to define mappings (tables to ORM classes --
        entities).

        """
        pass
