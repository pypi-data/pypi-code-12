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
Menus
"""

from django.conf import settings


_extra_menus = []
# collect menu from INSTALLED_APPS
for app in settings.INSTALLED_APPS:
    mod = __import__(app, fromlist=['ishtar_menu'])
    if hasattr(mod, 'ishtar_menu'):
        menu = getattr(mod, 'ishtar_menu')
        _extra_menus += menu.MENU_SECTIONS

# sort
__section_items = [mnu for order, mnu in sorted(_extra_menus,
                                                key=lambda x:x[0])]
# regroup menus
_section_items, __keys = [], []
for section_item in __section_items:
    if section_item.idx not in __keys:
        __keys.append(section_item.idx)
        _section_items.append(section_item)
        continue
    section_childs = _section_items[__keys.index(section_item.idx)].childs
    childs_idx = [child.idx for child in section_childs]
    for child in section_item.childs:
        if child.idx not in childs_idx:
            section_childs.append(child)


class Menu:
    childs = _section_items

    def __init__(self, user, current_action=None, session=None):
        self.user = user
        self.initialized = False
        self.items = {}
        self.current_action = current_action
        self.selected_idx = None
        self.session = session
        self.items_by_idx = {}

    def init(self):
        if self.initialized:
            return
        self.items = {}
        self.items_by_idx = {}
        for idx, main_menu in enumerate(self.childs):
            self.items_by_idx[main_menu.idx] = main_menu
            for child in main_menu.childs:
                self.items_by_idx[child.idx] = child
                if hasattr(child, 'childs'):
                    for subchild in child.childs:
                        self.items_by_idx[subchild.idx] = subchild
            selected = main_menu.set_items(
                self.user, self.items,
                self.current_action, session=self.session)
            if selected:
                self.selected_idx = idx
        self.initialized = True

menu = Menu(None)
menu.init()
