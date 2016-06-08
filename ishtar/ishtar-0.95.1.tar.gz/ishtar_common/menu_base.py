#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2012-2013 Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# See the file COPYING for details.

from ishtar_common.models import get_current_profile


class SectionItem:
    def __init__(self, idx, label, childs=[], profile_restriction=None):
        self.idx = idx
        self.label = label
        self.childs = childs
        self.available = False
        self.items = {}
        self.profile_restriction = profile_restriction

    def check_profile_restriction(self):
        if self.profile_restriction:
            profile = get_current_profile()
            if not getattr(profile, self.profile_restriction):
                return False
        return True

    def can_be_available(self, user, session=None):
        if not self.check_profile_restriction():
            return False
        for child in self.childs:
            if child.can_be_available(user, session=session):
                return True
        return False

    def is_available(self, user, obj=None, session=None):
        for child in self.childs:
            if child.is_available(user, obj, session=session):
                return True
        return False

    def set_items(self, user, items, current_action=None, session=None):
        selected = None
        if user:
            self.available = self.can_be_available(user, session=session)
        for child in self.childs:
            selected = child.set_items(user, items, current_action,
                                       session=session) or selected
            items[child.idx] = child
        return selected


class MenuItem:
    def __init__(self, idx, label, model=None, access_controls=[],
                 profile_restriction=None):
        self.idx = idx
        self.label = label
        self.model = model
        self.access_controls = access_controls
        self.available = False
        self.profile_restriction = profile_restriction
        if not self.check_profile_restriction():
            return False

    def check_profile_restriction(self):
        if self.profile_restriction:
            profile = get_current_profile()
            if not getattr(profile, self.profile_restriction):
                return False
        return True

    def can_be_available(self, user, session=None):
        if not self.check_profile_restriction():
            return False
        if not self.access_controls:
            return True
        prefix = (self.model._meta.app_label + '.') if self.model else ''
        for access_control in self.access_controls:
            access_control = prefix + access_control
            if hasattr(user, 'ishtaruser') and \
                user.ishtaruser.has_perm(access_control, self.model) or\
               access_control in user.get_group_permissions():
                #                         session=session) or \
                return True
        # manage by person type
        if hasattr(user, 'ishtaruser'):
            if user.ishtaruser.has_right(self.idx, session=session):
                return True
        return False

    def is_available(self, user, obj=None, session=None):
        if not self.check_profile_restriction():
            return False
        if not self.access_controls:
            return True
        prefix = (self.model._meta.app_label + '.') if self.model else ''
        for access_control in self.access_controls:
            access_control = prefix + access_control
            if user.has_perm(access_control, self.model, obj=obj):
                #              session=session):
                return True
        # manage by person type
        if hasattr(user, 'ishtaruser'):
            if user.ishtaruser.has_right(self.idx, session=session):
                return True
        return False

    def set_items(self, user, items, current_action=None, session=None):
        if user:
            self.available = self.can_be_available(user, session=session)
        if self.idx == current_action:
            return True
