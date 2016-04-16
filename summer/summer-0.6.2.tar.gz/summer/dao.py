# -*- coding: utf-8 -*-
# Time-stamp: < dao.py (2016-02-29 06:34) >

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

"""Provides *DAO* support.

Base :py:class:`Dao` class provides access to virtual
:py:attr:`Dao.session` and py:attr:`Dao.connection` attributes.

That means that inside any *DAO* object subclassed from :py:class:`Dao` you
can access current (thread-bound) *SQLAlchemy* session simply by accessing
:py:attr:`Dao.session` and direct connection to database by accessing
:py:attr:`Dao.connection`.  Alternatives are :py:meth:`Dao.get_session` and
:py:meth:`Dao.get_connection`.

Much more interesting is :py:class:`EntityDao` class which is inteded to be
used as a base *DAO* class for your :py:class:`summer.domain.Entity`.

"""

import logging

from sqlalchemy.engine import Connection
from sqlalchemy.orm import Query, Session
from sqlalchemy.orm.exc import NoResultFound

from .domain import Entity, Filter
from .ex import ApplicationException
from .sf import SessionFactory
from .txaop import transactional

logger = logging.getLogger(__name__)


class Dao(object):

    """Base *DAO* class.

    Provides safe access to thread bound session through :py:attr:`session`
    attribute.  Alternative is :py:meth:`get_session`.

    """

    def __init__(self, session_factory: SessionFactory):
        """Creates :py:class:`Dao` instance.

        Args:

            session_factory (SessionFactory): session factory to be used

        """
        self.session_factory = session_factory

    def __getattribute__(self, attrname: str):
        """Access to virtual :py:attr:`session` and :py:attr:`connection` attribute.

        """
        if attrname == "session":
            logger.debug("Dao.session access by '%s'", self)
            attrval = self.get_session()
        elif attrname == "connection":
            logger.debug("Dao.connection access by '%s'", self)
            attrval = self.get_connection()
        else:
            attrval = object.__getattribute__(self, attrname)
        return attrval

    def get_session(self) -> Session:
        """Get current session (bound to current thread).

        Returns:

            Session: current :py:class:`Session` instance
        """
        return self.session_factory.get_sqlalchemy_session()

    def get_connection(self) -> Connection:
        """Get current connection (bound to current thread).

        Use :py:data:`Dao.get_connection().connection` to obtain *Python DB
        API 2.0 connection* object.

        Returns:

            Connection: current :py:class:`Connection` instance

        """
        return self.session_factory.get_session().get_connection()


class EntityDao(Dao):

    """Base *DAO* class for persistent classes subclassed from
    :py:class:`summer.domain.Entity`.

    Provides basic persistent operations.

    Defines another virtual attribute -- :py:attr:`query` -- access to
    generic *SQLAlchemy* query over :py:attr:`clazz`.  Alternative is
    :py:meth:`get_query`.

    """

    def __init__(self, session_factory: SessionFactory, clazz: type):
        """Creates :py:class:`EntityDao` instance.

        Args:

            session_factory (SessionFactory): session factory intance to be
                                              passed to superclass
                                              (:py:class:`Dao`)

            clazz (type): reference to class type

        """
        Dao.__init__(self, session_factory)
        self.clazz = clazz

    def __getattribute__(self, attrname: str) -> object:
        """Access to virtual :py:attr:`query` attribute.

        """
        if attrname == "query":
            logger.debug("EntityDao.query access by '%s'", self)
            attrval = self.get_query()
        else:
            attrval = Dao.__getattribute__(self, attrname)
        return attrval

    def get_query(self) -> Query:
        """Get query over :py:attr:`clazz`.

        Returns:

            Query: :py:class:`Query` instance over :py:attr:`clazz`
        """
        return self.get_session().query(self.clazz)

    def _check_entity(self, entity: Entity):
        """Check if entity is correct.

        Args:

            entity (Entity): entity instance to be checked
        """
        if entity == None:
            raise DaoException("entity == None")
        elif not isinstance(entity, self.clazz):
            msg = "entity is not instance of %s" % self.clazz
            raise DaoException(msg, entity_class=entity.__class__)

    def _get_result_list(self, query: Query, query_filter: Filter) -> list:
        """Get list of entities with filter offset applied.  Useful for paging.

        Args:

            query (Query): query to be executed

            query_filter (Filter): filter to be used for paging

        Returns:

            list: list of entities using query and paging supplied

        """
        logger.debug("query %s", query)
        logger.debug("query_filter %s", query_filter)
        # apply query_filter limits
        query = query.offset(query_filter.get_offset())
        if query_filter.get_max_results() > 0:
            query = query.limit(query_filter.get_max_results())
        # query
        return query.all()

    @transactional
    def get(self, ident: object) -> Entity:
        """Get entity by :py:attr:`Entity.id` attribute.

        Args:

            ident (object): primary key for :py:class:`Entity`

        Returns:

            Entity: entity instance or raise :py:class:`NoResultFound` if
                    none is found

        """
        return self.query.populate_existing().get(ident)

    @transactional
    def save(self, entity: Entity) -> Entity:
        """Save an entity.

        Args:

            entity (Entity): entity to be persisted

        Returns:

            Entity: persisted instance

        """
        self._check_entity(entity)
        self.get_session().add(entity)
        return entity

    @transactional
    def merge(self, entity: Entity) -> Entity:
        """Merge an entity.

        Same as :py:meth:`save`, but entity is associated with current session
        if it is not.  For example if entity comes from another session
        (or thread).

        Args:

            entity (Entity): entity to be merged

        Returns:

            Entity: persisted instance

        """
        self._check_entity(entity)
        self.get_session().merge(entity)
        return entity

    @transactional
    def delete(self, entity_or_id: object) -> Entity:
        """Delete an entity.

        Args:

            entity_or_id (object): either :py:class:`Entity` or its primary
                                   key

        Returns:

            Entity: just deleted entity instance

        """
        if isinstance(entity_or_id, self.clazz):
            entity = entity_or_id
        else:
            entity = self.get(entity_or_id)
        self._check_entity(entity)
        self.get_session().delete(entity)
        return entity

    @transactional
    def find(self, query_filter: Filter) -> list:
        """Find collection of entities.

        Args:

            query_filter (Filter): filter with at least paging set

        Returns:

            list: list of entities using query and paging supplied
        """
        return self._get_result_list(self.query, query_filter)

    @transactional
    def get_by_uniq(self, col_name: str, col_value: object) -> Entity:
        """Get entity by its unique attribute value.

        Args:

            col_name (str): attribute column name

            col_value (object): attribute value


        Returns:

            Entity: entity instance or raise :py:class:`NoResultFound` if
                    none is found.

        """
        assert col_name != None, "col_name == None"
        assert col_value != None, "col_value == None"
        kwargs = {col_name: col_value}
        return self.query.filter_by(**kwargs).one()

    @transactional
    def get_by_uniq_or_none(self, col_name: str, col_value: object) -> Entity:
        """Get entity by its unique attribute value.

        Args:

            col_name (str): attribute column name

            col_value (object): attribute value


        Returns:

            Entity: entity instance or ``None`` if none is found.

        """
        try:
            tmp = self.get_by_uniq(col_name, col_value)
            return tmp
        except NoResultFound as e:
            logger.exception("no result found for %s having %s == %s",
                             self.clazz, col_name, col_value)
            return None


class CodeEntityDao(EntityDao):

    """Base *DAO* class for persistent classes subclassed from
    :py:class:`summer.domain.CodeEntity`.

    """

    def __init__(self, session_factory: SessionFactory, clazz: type):
        """Creates :py:class:`CodeEntityDao` instance.

        Args:

            session_factory (SessionFactory): session factory intance to be
                                              passed to superclass
                                              (:py:class:`Dao`)

            clazz (type): reference to class type

        """
        EntityDao.__init__(self, session_factory, clazz)

    @transactional
    def find_map(self, query_filter: Filter) -> dict:
        """Loads the objects into a map by :py:attr:`CodeEntity.code` attribute
        used as a map key.

            query_filter (Filter): filter with at least paging set

        Returns:

            dict: dictionary of entities using query and paging supplied

        """
        hash_map = dict()
        col = self.find(query_filter)
        for i in col:
            hash_map[i.code] = i
        return hash_map


class DaoException(ApplicationException):

    def __init__(self, message: str = None, **kwargs):
        ApplicationException.__init__(self, message, **kwargs)
