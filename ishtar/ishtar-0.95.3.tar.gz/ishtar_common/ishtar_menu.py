#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2010-2015 Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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
    (5, SectionItem('admin', _(u"Administration"),
     childs=[
        MenuItem('account_management', _(u"Account management"),
                 model=models.IshtarUser,
                 access_controls=['add_ishtaruser', ]),
        MenuItem('admin-globalvar', _(u"Global variables"),
                 model=models.GlobalVar,
                 access_controls=['add_globalvar', ]),
    ])
    ),
    (10, SectionItem('administration', _(u"Directory"),
     childs=[
        SectionItem(
            'person', _(u"Person"),
            childs=[
                MenuItem(
                    'person_search', _(u"Search"),
                    model=models.Person,
                    access_controls=['add_person']),
                MenuItem(
                    'person_creation', _(u"Creation"),
                    model=models.Person,
                    access_controls=['add_person']),
                MenuItem(
                    'person_modification', _(u"Modification"),
                    model=models.Person,
                    access_controls=['change_person', 'change_own_person']),
                MenuItem(
                    'person_merge', _(u"Merge"),
                    model=models.Person,
                    access_controls=['merge_person']),
                MenuItem(
                    'person_deletion', _(u"Delete"),
                    model=models.Person,
                    access_controls=['change_person', 'change_own_person']),
            ]),
        SectionItem(
            'organization', _(u"Organization"),
            childs=[
                MenuItem(
                    'organization_search', _(u"Search"),
                    model=models.Organization,
                    access_controls=['add_organization',
                                     'add_own_organization']),
                MenuItem(
                    'organization_creation', _(u"Creation"),
                    model=models.Organization,
                    access_controls=['add_organization',
                                     'add_own_organization']),
                MenuItem(
                    'organization_modification', _(u"Modification"),
                    model=models.Organization,
                    access_controls=['change_organization',
                                     'change_own_organization']),
                MenuItem(
                    'organization_merge', _(u"Merge"),
                    model=models.Organization,
                    access_controls=['merge_organization']),
                MenuItem(
                    'organization_deletion', _(u"Delete"),
                    model=models.Organization,
                    access_controls=['change_organization',
                                     'change_own_organization']),
            ]),
    ])
    ),
    (15, SectionItem(
        'imports', _(u"Imports"),
        childs=[
            MenuItem(
                'import-new', _(u"New import"),
                model=models.Import,
                access_controls=['change_import']),
            MenuItem(
                'import-list', _(u"Current imports"),
                model=models.Import,
                access_controls=['change_import']),
            MenuItem(
                'import-list-old', _(u"Old imports"),
                model=models.Import,
                access_controls=['change_import']),
        ])),
]
