#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2010-2016 Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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

from archaeological_operations.models import AdministrativeAct

import models

# be carreful: each access_controls must be relevant with check_rights in urls

MENU_SECTIONS = [
    (20,
     SectionItem(
         'file_management', _(u"Archaeological file"),
         profile_restriction='files',
         childs=[
             MenuItem(
                 'file_search', _(u"Search"),
                 model=models.File,
                 access_controls=['view_file', 'view_own_file']),
             MenuItem(
                 'file_creation', _(u"Creation"),
                 model=models.File,
                 access_controls=['add_file', 'add_own_file']),
             MenuItem(
                 'file_modification', _(u"Modification"),
                 model=models.File,
                 access_controls=['change_file', 'change_own_file']),
             MenuItem(
                 'file_closing', _(u"Closing"),
                 model=models.File,
                 access_controls=['close_file']),
             MenuItem(
                 'file_deletion', _(u"Deletion"),
                 model=models.File,
                 access_controls=['delete_file', 'delete_own_file']),
             SectionItem(
                 'admin_act_files', _(u"Administrative act"),
                 childs=[
                     MenuItem('file_administrativeactfil_search',
                              _(u"Search"),
                              model=AdministrativeAct,
                              access_controls=['change_administrativeact']),
                     MenuItem('file_administrativeactfil',
                              _(u"Add"),
                              model=AdministrativeAct,
                              access_controls=['change_administrativeact']),
                     MenuItem('file_administrativeactfil_modification',
                              _(u"Modification"),
                              model=AdministrativeAct,
                              access_controls=['change_administrativeact']),
                     MenuItem('file_administrativeactfil_deletion',
                              _(u"Deletion"),
                              model=AdministrativeAct,
                              access_controls=['change_administrativeact']),
                     MenuItem('file_administrativeact_document',
                              _(u"Documents"),
                              model=AdministrativeAct,
                              access_controls=['change_administrativeact']),
                 ],)]),),
    (100,
     SectionItem(
         'dashboard', _(u"Dashboard"),
         profile_restriction='files',
         childs=[MenuItem('dashboard_main', _(u"General informations"),
                          model=models.File,
                          access_controls=['change_file', 'change_own_file']),
                 MenuItem('dashboard_file', _(u"Archaeological files"),
                          model=models.File,
                          access_controls=['change_file', 'change_own_file']),
                 ]),
     ),
]
"""
        SectionItem('dashboard', _(u"Dashboard"),
            childs=[
                    MenuItem('dashboard_main', _(u"General informations"),
                        model=models.File,
                        access_controls=['change_file', 'change_own_file']),
                    MenuItem('dashboard_file', _(u"Archaeological files"),
                        model=models.File,
                        access_controls=['change_file', 'change_own_file']),
                    #MenuItem('dashboard_treatment', _(u"Treatments"),
                    #   model=models.Treatment,
                    #    access_controls=['change_treatment',]),
                    #MenuItem('dashboard_warehouse', _(u"Warehouses"),
                    #    model=models.Warehouse,
                    #    access_controls=['change_warehouse',]),
            ]),
        ]
"""
