#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2012-2016 Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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

from django.utils.translation import ugettext_lazy as _

from ishtar_common.menu_base import SectionItem, MenuItem

import models

# be carreful: each access_controls must be relevant with check_rights in urls

MENU_SECTIONS = [
    (50,
     SectionItem(
         'find_management', _(u"Find"),
         profile_restriction='find',
         childs=[
             MenuItem(
                 'find_search', _(u"Search"),
                 model=models.Find,
                 access_controls=['view_find',
                                  'view_own_find']),
             MenuItem(
                 'find_creation', _(u"Creation"),
                 model=models.Find,
                 access_controls=['add_find',
                                  'add_own_find']),
             MenuItem(
                 'find_modification', _(u"Modification"),
                 model=models.Find,
                 access_controls=['change_find',
                                  'change_own_find']),
             # MenuItem('treatment_creation', _(u"Add a treatment"),
             #     model=models.Treatment,
             #     access_controls=['add_treatment',
             #                      'add_own_treatment']),
             MenuItem(
                 'find_deletion', _(u"Deletion"),
                 model=models.Find,
                 access_controls=['change_find',
                                  'change_own_find']),
             SectionItem(
                 'find_basket', _(u"Basket"),
                 childs=[
                     MenuItem('find_basket_creation',
                              _(u"Creation"),
                              model=models.FindBasket,
                              access_controls=['change_find',
                                               'change_own_find']),
                     MenuItem('find_basket_modification_add',
                              _(u"Manage items"),
                              model=models.FindBasket,
                              access_controls=[
                                  'change_find',
                                  'change_own_find']),
                     MenuItem('find_basket_deletion',
                              _(u"Deletion"),
                              model=models.FindBasket,
                              access_controls=['change_find',
                                               'change_own_find']),
                 ]),
             SectionItem(
                 'find_source', _(u"Documentation"),
                 childs=[
                     MenuItem('find_source_creation',
                              _(u"Creation"),
                              model=models.FindSource,
                              access_controls=['change_find',
                                               'change_own_find']),
                     MenuItem('find_source_modification',
                              _(u"Modification"),
                              model=models.FindSource,
                              access_controls=['change_find',
                                               'change_own_find']),
                     MenuItem('find_source_deletion',
                              _(u"Deletion"),
                              model=models.FindSource,
                              access_controls=['change_find',
                                               'change_own_find']),
                 ])
         ]))
]
