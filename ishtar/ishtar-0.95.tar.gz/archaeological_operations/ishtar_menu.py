#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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

from django.utils.translation import ugettext_lazy as _, pgettext_lazy

from ishtar_common.menu_base import SectionItem, MenuItem

import models

# be carreful: each access_controls must be relevant with check_rights in urls

MENU_SECTIONS = [
    (30, SectionItem(
        'operation_management', _(u"Operation"),
        childs=[
            MenuItem(
                'operation_search', _(u"Search"),
                model=models.Operation,
                access_controls=['view_operation',
                                 'view_own_operation']),
            MenuItem(
                'operation_creation', _(u"Creation"),
                model=models.Operation,
                access_controls=['add_operation',
                                 'add_own_operation']),
            MenuItem(
                'operation_modification', _(u"Modification"),
                model=models.Operation,
                access_controls=['change_operation',
                                 'change_own_operation']),
            MenuItem(
                'operation_closing', _(u"Closing"),
                model=models.Operation,
                access_controls=['close_operation']),
            MenuItem(
                'operation_deletion', _(u"Deletion"),
                model=models.Operation,
                access_controls=['change_operation',
                                 'change_own_operation']),
            SectionItem(
                'admin_act_operations',
                _(u"Administrative act"),
                profile_restriction='files',
                childs=[
                    MenuItem(
                        'operation_administrativeactop_search',
                        _(u"Search"),
                        model=models.AdministrativeAct,
                        access_controls=[
                            'change_administrativeact']),
                    MenuItem(
                        'operation_administrativeactop',
                        _(u"Add"),
                        model=models.AdministrativeAct,
                        access_controls=['change_administrativeact']),
                    MenuItem(
                        'operation_administrativeactop_modification',
                        _(u"Modification"),
                        model=models.AdministrativeAct,
                        access_controls=['change_administrativeact']),
                    MenuItem(
                        'operation_administrativeactop_deletion',
                        _(u"Deletion"),
                        model=models.AdministrativeAct,
                        access_controls=['change_administrativeact']),
                    MenuItem(
                        'operation_administrativeact_document',
                        _(u"Documents"),
                        model=models.AdministrativeAct,
                        access_controls=['change_administrativeact']),
                ],),
            SectionItem(
                'operation_source', _(u"Documentation"),
                childs=[
                    MenuItem('operation_source_search',
                             _(u"Search"),
                             model=models.OperationSource,
                             access_controls=['view_operation',
                                              'view_own_operation']),
                    MenuItem('operation_source_creation',
                             _(u"Add"),
                             model=models.OperationSource,
                             access_controls=['change_operation',
                                              'change_own_operation']),
                    MenuItem('operation_source_modification',
                             _(u"Modification"),
                             model=models.OperationSource,
                             access_controls=['change_operation',
                                              'change_own_operation']),
                    MenuItem('operation_source_deletion',
                             _(u"Deletion"),
                             model=models.OperationSource,
                             access_controls=['change_operation',
                                              'change_own_operation']),
                ])
        ]),
     ),
    (
        35, SectionItem(
            'administrativact_management', _(u"Administrative Act"),
            profile_restriction='files',
            childs=[
                MenuItem(
                    'administrativact_register',
                    pgettext_lazy('admin act register', u"Register"),
                    model=models.AdministrativeAct,
                    access_controls=['view_administrativeact',
                                     'view_own_administrativeact']),
            ])
    ),
    (
        102, SectionItem(
            'dashboard', _(u"Dashboard"),
            childs=[
                MenuItem(
                    'dashboard_main', _(u"General informations"),
                    model=models.Operation,
                    access_controls=['change_operation']),
                MenuItem(
                    'dashboard_operation', _(u"Operations"),
                    model=models.Operation,
                    access_controls=['change_operation']),
            ]),
    ),
]
