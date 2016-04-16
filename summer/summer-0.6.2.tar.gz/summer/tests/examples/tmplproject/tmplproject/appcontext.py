# -*- coding: utf-8 -*-
# Time-stamp: < appcontext.py (2016-02-12 08:13) >

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

"""
Application context definition.
"""

import logging

# configure logging as soon as possible
logger = logging.getLogger(__name__)

import summer

# do all the necessary imports, all that is imported bellow is deployed
# into the context, just as an example -- you can deploy anything you want
# of course
from .cmdline import MyOptionParser
from .orm.tables import TableDefinitions
from .orm.mappings import ClassMappings
from .manager import (
    CategoryDao, CategoryManager,
    ItemDao, ItemManager,
    UserDao, UserManager,
)


class ApplicationContext(summer.Context):

    def __init__(self, path_to_module, customcfg):
        summer.Context.__init__(self, path_to_module, customcfg)

    def orm_init(self):
        # you can do whatever setup you want, here you can see so-called
        # "classical" mapping, see SQLAlchemy for details

        # first let's complete database initialization with custom table
        # definitions and mappings
        self.session_factory.set_table_definitions(TableDefinitions())
        # class mappings must be defined _after_ table definitions
        self.session_factory.set_class_mappings(ClassMappings())

    def context_init(self):

        # create command line parser, pass it reference of our custom
        # config to guess the correct defaults
        self.my_option_parser = MyOptionParser(self.config)

        # let's deploy SQL DAO's with corresponding proxies -- use proxy
        # object whenever you want a separate transaction, use non-proxied
        # version as a 'building block' when you need to take part in
        # on-going transaction
        self.category_dao = CategoryDao(self.session_factory)
        self.category_dao_proxy = summer.TransactionProxy(self.category_dao)
        self.item_dao = ItemDao(self.session_factory)
        self.item_dao_proxy = summer.TransactionProxy(self.item_dao)

        # let's deploy LDAP DAO's; treat them as analogy to SQL DAO's,
        # though the LDAP has no sense of SQL transaction
        self.user_dao = UserDao(self.ldap_session_factory)
        self.user_dao_proxy = summer.LdapProxy(self.user_dao)

        # let's define some higher level business level objects (managers)
        self.category_manager = CategoryManager(self.category_dao)
        self.category_manager_proxy = \
            summer.TransactionProxy(self.category_manager,
                                    self.session_factory)
        self.item_manager = ItemManager(self.item_dao)
        self.item_manager_proxy = summer.TransactionProxy(self.item_manager,
                                                          self.session_factory)
        self.user_manager = UserManager(self.user_dao)
        self.user_manager_proxy = summer.LdapProxy(self.user_manager,
                                                   self.ldap_session_factory)
