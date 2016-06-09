#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2012 Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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

from archaeological_finds.models import Treatment

# be carreful: each access_controls must be relevant with check_rights in urls


MENU_SECTIONS = [
    (60, SectionItem('find_management', _(u"Find"),
     profile_restriction='warehouse',
     childs=[
        MenuItem('warehouse_packaging', _(u"Packaging"),
                 model=Treatment,
                 access_controls=['add_treatment', 'add_own_treatment']),
    ])),
]
"""
    (60, SectionItem('warehouse', _(u"Warehouse"),
        childs=[
                MenuItem('warehouse_inventory', _(u"Inventory"),
                    model=models.Warehouse,
                    access_controls=['change_warehouse',]),
                MenuItem('warehouse_recording', _(u"Recording"),
                    model=Treatment,
                    access_controls=['add_treatment', 'add_own_treatment']),
                MenuItem('warehouse_lend', _(u"Lending"),
                    model=Treatment,
                    access_controls=['add_treatment', 'add_own_treatment']),
        ]))
"""
