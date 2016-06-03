#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2010-2013 Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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

"""
Permission backend to manage "own" objects
"""

from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.loading import cache

import models


class ObjectPermBackend(ModelBackend):
    supports_object_permissions = True
    supports_anonymous_user = True

    def has_perm(self, user_obj, perm, model=None, obj=None, session=None):
        if not user_obj.is_authenticated():
            return False
        if not model:
            # let it manage by the default backend
            return False
        try:
            ishtar_user = models.IshtarUser.objects.get(user_ptr=user_obj)
        except ObjectDoesNotExist:
            return False
        try:
            is_ownperm = perm.split('.')[-1].split('_')[1] == 'own'
        except IndexError:
            is_ownperm = False
        if ishtar_user.has_right('administrator', session=session):
            return True
        main_right = ishtar_user.person.has_right(perm, session=session) \
            or user_obj.has_perm(perm)
        if not main_right or not is_ownperm:
            return main_right
        if obj is None:
            model_name = perm.split('_')[-1].lower()
            model = None
            for app in cache.get_apps():
                for modl in cache.get_models(app):
                    if modl.__name__.lower() == model_name:
                        model = modl
            if not model:
                return False
            return not is_ownperm or model.has_item_of(ishtar_user)
        return not is_ownperm or obj.is_own(user_obj)
