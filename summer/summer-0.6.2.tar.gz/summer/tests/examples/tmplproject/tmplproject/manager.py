# -*- coding: utf-8 -*-
# Time-stamp: < manager.py (2016-02-14 09:49) >

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

import ldap3

from summer import CodeEntityDao, transactional
from summer import LdapEntityDao, ldapaop

from .model import Category, Item, User

#
# category #
#


class CategoryDao(CodeEntityDao):

    def __init__(self, session_factory):
        CodeEntityDao.__init__(self, session_factory, Category)

    @transactional
    def sample_method1(self):
        pass

    @transactional
    def sample_method2(self):
        pass


class CategoryManager(object):

    def __init__(self, category_dao):
        self.category_dao = category_dao

    @transactional
    def sample_method3(self):
        pass

#
# item #
#


class ItemDao(CodeEntityDao):

    def __init__(self, session_factory):
        CodeEntityDao.__init__(self, session_factory, Item)

    @transactional
    def sample_method1(self):
        pass

    @transactional
    def sample_method2(self):
        pass


class ItemManager(object):

    def __init__(self, item_dao):
        self.item_dao = item_dao

    @transactional
    def sample_method3(self):
        pass

#
# user #
#


class UserDao(LdapEntityDao):

    def __init__(self, ldap_session_factory):
        LdapEntityDao.__init__(self, ldap_session_factory, User)

    @ldapaop
    def find(self):
        """Gets all users."""
        session = self.session
        base = "ou=users,%s" % (self.base,)
        result = session.search(search_base=base,
                                search_filter="(cn=*)",
                                search_scope=ldap3.SEARCH_SCOPE_WHOLE_SUBTREE,
                                attributes=["cn", "userPassword"])
        users = list()
        if result:
            for entry in session.response:
                attrs = entry["attributes"]
                login = attrs["cn"][0]
                crypt = attrs["userPassword"][0]
                user = User(login, crypt)
                users.append(user)
        return users


class UserManager(object):

    def __init__(self, user_dao):
        self.user_dao = user_dao

    @ldapaop
    def find(self):
        return self.user_dao.find()
