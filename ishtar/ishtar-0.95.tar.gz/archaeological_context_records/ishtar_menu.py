#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012 Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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
    (40, SectionItem('record_management', _(u"Context record"),
     profile_restriction='context_record',
     childs=[MenuItem('record_search', _(u"Search"),
             model=models.ContextRecord,
             access_controls=['view_contextrecord',
                              'view_own_contextrecord']),
             MenuItem('record_creation', _(u"Creation"),
             model=models.ContextRecord,
             access_controls=['add_contextrecord',
                              'add_own_contextrecord']),
             MenuItem('record_modification', _(u"Modification"),
             model=models.ContextRecord,
             access_controls=['change_contextrecord',
                              'change_own_contextrecord']),
             MenuItem('record_deletion', _(u"Deletion"),
             model=models.ContextRecord,
             access_controls=['delete_contextrecord',
                              'delete_own_contextrecord']),
             SectionItem('record_source', _(u"Documentation"),
                         childs=[
                         MenuItem('record_source_creation',
                                  _(u"Add"),
                                  model=models.ContextRecordSource,
                                  access_controls=[
                                      'change_contextrecord',
                                      'change_own_contextrecord']),
                         MenuItem('record_source_modification',
                                  _(u"Modification"),
                                  model=models.ContextRecordSource,
                                  access_controls=[
                                      'change_contextrecord',
                                      'change_own_contextrecord']),
                         MenuItem('record_source_deletion',
                                  _(u"Deletion"),
                                  model=models.ContextRecordSource,
                                  access_controls=[
                                      'change_contextrecord',
                                      'change_own_contextrecord']),
                         ])
             ])
     )
]
