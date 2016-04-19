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

from django.conf.urls.defaults import *

# from ishtar_common.wizards import check_rights
import views

# be carreful: each check_rights must be relevant with ishtar_menu

# forms
urlpatterns = patterns(
    '',
    # url(r'treatment_creation/(?P<step>.+)?$',
    #    views.treatment_creation_wizard, name='treatment_creation'),
    url(r'warehouse_packaging/(?P<step>.+)?$',
        views.warehouse_packaging_wizard, name='warehouse_packaging'),
)

urlpatterns += patterns(
    'archaeological_warehouse.views',
    url(r'new-warehouse/(?P<parent_name>.+)?/$',
        'new_warehouse', name='new-warehouse'),
    url(r'autocomplete-warehouse/$', 'autocomplete_warehouse',
        name='autocomplete-warehouse'),
    url(r'new-container/(?P<parent_name>.+)?/$',
        'new_container', name='new-container'),
    url(r'get-container/$', 'get_container',
        name='get-container'),
    url(r'autocomplete-container/?$',
        'autocomplete_container', name='autocomplete-container'),
)
