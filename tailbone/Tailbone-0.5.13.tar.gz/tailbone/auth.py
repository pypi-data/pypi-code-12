# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2015 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Authentication & Authorization
"""

from __future__ import unicode_literals

from edbob.util import prettify

from rattail.db import model
from rattail.db.auth import has_permission

from zope.interface import implementer
from pyramid.interfaces import IAuthorizationPolicy
from pyramid.security import Everyone, Authenticated

from tailbone.db import Session


@implementer(IAuthorizationPolicy)
class TailboneAuthorizationPolicy(object):

    def permits(self, context, principals, permission):
        for userid in principals:
            if userid not in (Everyone, Authenticated):
                user = Session.query(model.User).get(userid)
                if user:
                    return has_permission(Session(), user, permission)
        if Everyone in principals:
            return has_permission(Session(), None, permission)
        return False

    def principals_allowed_by_permission(self, context, permission):
        raise NotImplementedError


def add_permission_group(config, key, label=None, overwrite=True):
    """
    Add a permission group to the app configuration.
    """
    def action():
        perms = config.get_settings().get('tailbone_permissions', {})
        if key not in perms or overwrite:
            group = perms.setdefault(key, {'key': key})
            group['label'] = label or prettify(key)
        config.add_settings({'tailbone_permissions': perms})
    config.action(None, action)


def add_permission(config, groupkey, key, label=None):
    """
    Add a permission to the app configuration.
    """
    def action():
        perms = config.get_settings().get('tailbone_permissions', {})
        group = perms.setdefault(groupkey, {'key': groupkey})
        group.setdefault('label', prettify(groupkey))
        perm = group.setdefault('perms', {}).setdefault(key, {'key': key})
        perm['label'] = label or prettify(key)
        config.add_settings({'tailbone_permissions': perms})
    config.action(None, action)
