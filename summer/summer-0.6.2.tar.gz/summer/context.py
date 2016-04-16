# -*- coding: utf-8 -*-
# Time-stamp: < context.py (2016-02-14 02:25) >

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

"""Module ``context`` defines an application context (:py:class:`Context`
class)-- a container for (business) objects, that should be available
throughout the application, application layer or module.

"""

from configparser import SafeConfigParser
import logging
import os

from . import l10n
from . import lsf
from . import sf
from . import utils
from .ex import (
    SummerConfigurationException,
    NoObjectFoundException,
)

logger = logging.getLogger(__name__)

# summer config sections
SQLALCHEMY = "SQLALCHEMY"
L10N = "L10N"
LDAP = "LDAP"


class Context(object):

    """Context is inteligent container for your business objects, it is a core
    of *summer framework*.

    It is responsible for:

    #. summer framework initialization (reading config files)
    #. instantiating your business classes with their interdependencies
    #. proxy creation

    It uses convention over configuration approach, so it supposes specific
    config file names etc, though much of it may be overwritten.

    Emulates mapping type, so you can access business objects by their name
    if required.

    Usually in medium sized applications, you define single global context
    somewhere in main entry point of your program.

    """

    def __init__(self,
                 path_to_module: str,
                 customcfg: str=None,
                 summercfg: str='summer.cfg'):
        """Context initialization is separated into several steps:

        #. call :py:meth:`core_init` (not indended to be overriden) which
           parses config files and creates core objects managing key
           resources (sql database, ldap server, localization)

        #. call :py:meth:`orm_init` (intended to be overriden) which
           initializes ORM

        #. call :py:meth:`context_init` (intended to be overriden) -- a
           place to define your business beans

        Args:

            path_to_module (str): path to module, usually pass ``__file__``
                                  built-in.  It will look for config files
                                  up to several directories levels up.

            customcfg (str): name of custom config file

            summercfg (str): name of summer config file

        """

        logger.info("context initialization started")
        self.path_to_module = path_to_module
        self.customcfg = customcfg
        self.summercfg = summercfg

        self.summer_config = None
        self.session_factory = None
        self.ldap_session_factory = None
        self.l10n = None
        self.config = None

        logger.info("initializing core services")
        self.core_init()
        logger.info("core services initialized")

        logger.info("initializing orm")
        self.orm_init()
        logger.info("orm initialized")

        logger.info("custom context initialization started")
        self.context_init()
        logger.info("custom context initialization done")

        logger.info("context initialization done")

    def __del__(self):
        """Calls :py:meth:`context_shutdown` to properly shutdown the context."""
        self.context_shutdown()

    def core_init(self):
        """Initializes core objects based on :py:attr:`summer_config`."""
        # summer config
        self.summer_config = SafeConfigParser()
        self.summer_config.read(
            utils.locate_file(self.path_to_module, self.summercfg))
        # session factory
        logger.info("creating session factory")
        self.session_factory = self._create_session_factory()
        logger.info("session factory created %s", self.session_factory)
        # ldap_session_facory
        logger.info("creating ldap session factory")
        self.ldap_session_factory = self._create_ldap_session_factory()
        logger.info("ldap session factory created %s",
                    self.ldap_session_factory)
        # l10n
        logger.info("creating l10n services")
        self.l10n = self._create_l10n()
        logger.info("l10n services created %s", self.l10n)
        # custom config
        if self.customcfg != None:
            logger.info("loadig custom config file")
            self.config = SafeConfigParser()
            self.config.read(
                utils.locate_file(self.path_to_module, self.customcfg))
            logger.info("custom config file loaded %s", self.config)

    def _create_session_factory(self, **kwargs):
        """Can be overridden by subclasses (if ORM is in use).  Creates session
        factory.

        Arguments:

            kwargs (dict): passed directly to
                           :py:class:`summer.sf.SessionFactory`

        Returns:

            SessionFactory: :py:class:`summer.sf.SessionFactory` instance.

        """
        config = self.summer_config
        session_factory = None
        if config.has_section(SQLALCHEMY):
            uri = config.get(SQLALCHEMY, "uri")
            echo = config.getboolean(SQLALCHEMY, "echo")
            autoflush = config.getboolean(SQLALCHEMY, "autoflush")
            autocommit = config.getboolean(SQLALCHEMY, "autocommit")
            session_factory = sf.SessionFactory(uri,
                                                echo,
                                                autoflush,
                                                autocommit,
                                                **kwargs)
        else:
            logger.info("session factory not initialized -- no config")
        return session_factory

    def _create_ldap_session_factory(self):
        """Can be overriden by subclasses (if LDAP is in use).  Creates ldap session
        factory.

        Returns:

            LdapSessionFactory: :py:class:`summer.lsf.LdapSessionFactory` instance.

        """
        config = self.summer_config
        ldap_session_factory = None
        if config.has_section(LDAP):
            hostname = config.get(LDAP, "hostname")
            port = config.getint(LDAP, "port")
            base = config.get(LDAP, "base")
            login = config.get(LDAP, "login")
            passwd = config.get(LDAP, "passwd")
            ldap_session_factory = lsf.LdapSessionFactory(hostname,
                                                          port,
                                                          base,
                                                          login,
                                                          passwd)
        else:
            logger.info("ldap session factory not initialized -- no config")
        return ldap_session_factory

    def _create_l10n(self):
        """Can be overriden by subclasses (if localization is in use).  Creates
        l10n.

        Returns:

            Localization: :py:class:`summer.l10n.Localization` instance.

        """
        config = self.summer_config
        localization = None
        if config.has_section(L10N):
            domain = config.get(L10N, "domain")
            l10n_dir = config.get(L10N, "l10n_dir")
            languages = str(config.get(L10N, "languages")).split(",")
            if not os.access(l10n_dir, os.F_OK):
                logger.warning("not found path '%s'", l10n_dir)
                l10n_dir = utils.locate_file(self.path_to_module, l10n_dir)
                if not os.access(l10n_dir, os.F_OK):
                    raise SummerConfigurationException(l10n_dir=l10n_dir)
            localization = l10n.Localization(domain, l10n_dir, languages)
        else:
            logger.info("localization not initialized -- no config")
        return localization

    def orm_init(self):
        """Should be overriden by subclasses to initialize ORM managed tables and
        class mappings.

        You should define your custom table definitions based on
        :py:class:`summer.sf.AbstractTableDefinitions` and mappings based
        on :py:class:`summer.sf.AbstractClassMappings`.

        Usually you have just those lines there::

            self.session_factory.set_table_definitions(TableDefinitions())
            self.session_factory.set_class_mappings(ClassMappings())

        """
        pass

    def context_init(self):
        """Should be overriden by subclasses to initialize custom objects in
        context.

        This is the last stage of context initialization, this method gets called after

        #. :py:meth:`core_init`
        #. :py:meth:`orm_init`

        are called.  You can safely access those attributes:

        * :py:attr:`summer_config` -- Python's
          :py:class:`configparser.SafeConfigParser` instance of the summer
          framework itself

        * :py:attr:`config` -- Python's
          :py:class:`configparser.SafeConfigParser` of your custom config
          (if provided)

        * :py:attr:`l10n` -- :py:class:`summer.l10n.Localization` instance,
          not very interesting in itself, but summer's localization module
          installs the famous :py:meth:`_` gettext function into global
          namespace (as normal gettext module does) and configures your
          localization based on whatever you provided in *summer* framework
          config (:py:attr:`summer_config` attribute)

        * :py:attr:`session_factory` --
          :py:class:`summer.sf.SessionFactory` instance, which provides
          thread-safe access to :py:class:`sqlalchemy.session` -- any data
          aware object (ie. each DAO at least) should have access to it.
          By convention, name all the references to this object as
          **session_factory**.  AOP depends on this.  You can override it,
          but why would you do it?  Remember: *convention over
          configuration*.

        * :py:attr:`ldap_session_factory`
          :py:class:`summer.lsf.LdapSessionFactory` instance, which
          provides thread-safe access to
          :py:class:`summer.lsf.LdapSessionFactory.Local` instance -- a
          simple wrapper around actual :py:class:`ldap3.Connection`, again,
          convention dictates to name reference to this object as
          **ldap_session_factory**.  AOP depends on this.

        """
        pass

    def context_shutdown(self):
        """Handles context shutdown.  Called from :py:meth:`__del__`."""
        # FIXME martin.slouf -- ValueError is thrown by Python stdlib?!
        # logger.info("context shutdown")
        pass

    def __len__(self):
        return len(self.__dict__)

    def __getitem__(self, key):
        if key in self.__dict__:
            return self.__dict__[key]
        else:
            raise NoObjectFoundException(object_name=key)

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __delitem__(self, key):
        del self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__)
