# -*- coding: utf-8 -*-
# Time-stamp: < appcontext.py (2016-02-14 03:16) >

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

"""This module demonstrates the very core usage of the *summer* application
framework.

For people familiar with Java spring framework -- this file defines the
:py:class:`ApplicationContext` class.  All configuration is placed directly
in your *Python* code.

Among other resources somewhere in your application you will have a file
like this -- a file defining a 'context' for your application business
layer.  You can of course have more layers, more contexts, ...

Such a context class serves as a container for your business objects.  Once
you have you context initialized, you may usually access all your
application's services from one single place.  The best is, that all the
creation, dependency and initialization logic among your business objects
is defined there.

Objects deployed into the context should be stateless and can be treated as
singletons (but there is no rule for that and you can deploy whatever you
want in any way you like it) -- please see any discussion on inversion of
control containers (IoC) for more info.

This simple example shows:

  1. sample context definition with very simple declarative transaction
  handling

  2. basic concept how to use logging and custom configuration files --
  logging config (defined by Python stdlib), summer framework config
  (including database connection definition) and custom config for your
  project

  3. So you get an idea, what its all about :-)

"""

# usual imports
import configparser
import logging
import optparse

# import the summer framework
import summer

# reasonable and simple convention on getting a logger
logger = logging.getLogger(__name__)


class OptionParser(optparse.OptionParser):

    """Command line parser.

    This class has access to custom config to appropriately set the default
    values based on options defined, if required.

    """

    def __init__(self, config: configparser.ConfigParser):
        optparse.OptionParser.__init__(self)
        self.config = config
        verbose = self.config.getboolean("DEFAULT", "verbose")
        self.add_option(
            "-v", "--verbose",
            action="store_true",
            dest="verbose",
            default=verbose,
            help="[GLOBAL] make lots of noise [default: %default]"
        )


class Entity(summer.Entity):

    """Entities are usually ORM mapped classes :py:class:`summer.domain.Entity`"""
    pass


class EntityDao(summer.Dao):

    """Dao object for our :py:class:`Entity`.

    Entity persistence logic is usually managed by a Dao object; usually
    you will subclass those provided by *summer*, see
    :py:class:`summer.dao.Dao` for details.

    """

    def __init__(self, session_factory):
        summer.Dao.__init__(self, session_factory)

    @summer.transactional
    def find(self, filter):
        """Dao methods are usually declared as transactional.  That does not say
        they always run in separate transaction, but it says that such a
        method can be run in transaction if run inside a transactional
        proxy :py:class:`summer.txaop.TransactionalProxy`.

        """
        pass


class EntityManager(object):

    """This class manages entities using the Dao, probably it adds some
    business logic for creating a new object and such.

    """

    def __init__(self, entity_dao):
        pass

    @summer.transactional
    def create_entity(self, entity):
        """Method is marked as transactional.  See below how transactional proxy is
        created.

        """
        logger.info("creating new entity")


class ApplicationContext(summer.Context):

    """The much anticipated application context class."""

    def __init__(self, path_to_module, customcfg):
        """:py:class:`summer.context.Context` has some more arguments, but usually
        those 2 are the only ones required, as the others defaults to
        reasonable values.  In most cases it is safe to pass ``__file__``
        as ``path_to_module``.

        """
        summer.Context.__init__(self, path_to_module, customcfg)

    def orm_init(self):
        """Do additional ORM setup for your application.  For now, just ignore
        it.

        """
        # you can do whatever setup you want, here you can see so-called
        # "classical" mapping, see *SQLAlchemy* for details

        # first let's complete database initialization with custom table
        # definitions and mappings
        # self.session_factory.set_table_definitions(TableDefinitions())

        # class mappings must be defined *after* table definitions
        # self.session_factory.set_class_mappings(ClassMappings())

        pass

    def context_init(self):
        """Please see :py:method:`summer.context.Context.context_init`.

        This method gets called once the basic context initialization is
        done.  You may deploy your business objects there.

        """

        # we deploy our command line parser -- which accesses some settings
        # from our config file, so it holds a reference to it
        self.option_parser = OptionParser(self.config)

        # lets deploy our only DAO -- any data access object should have a
        # reference to session factory to obtain session from it any time
        # it accesses data
        self.entity_dao = EntityDao(self.session_factory)
        # also any data aware object, that has some transactional methods,
        # can be deployed as transactional proxy, the proxy itself accesses
        # the session factory, but is capable to obtain it from the target
        # object -- no need to pass it as a constructor arg -- there is a
        # very simple convention -- it just looks for 'session_factory'
        # attribute in the target object (ie. our DAO)
        self.entity_dao_proxy = summer.TransactionProxy(self.entity_dao)

        # the same applies for EntityManager as for EntityDao, we deploy
        # the non-proxied dao and as it defines its own transaction
        # boundaries we deploy also a transaction proxy.  We should provide
        # the session factory now, because the detection mechanism is not
        # very smart and just checks for an attribute named
        # 'session_factory' inside a target object as said earlier and
        # apparently EntityManager class has no such attribute
        self.entity_manager = EntityManager(self.entity_dao)
        self.entity_manager_proxy = summer.TransactionProxy(
            self.entity_manager,
            self.session_factory)
