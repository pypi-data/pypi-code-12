#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2014 Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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

from archaeological_files_pdl import views

urlpatterns = patterns(
    '',
    url(r'file_creation/(?P<step>.+)?$',
        views.file_creation_wizard, name='file_creation'),
    url(r'file_modification/(?P<step>.+)?$',
        views.file_modification_wizard, name='file_modification'),
    url(r'townplanning-edit/$',
        views.TownPlanningCreate.as_view(),
        name='townplanning_create'),
    url(r'townplanning-edit/(?P<pk>\d+)$',
        views.TownPlanningEdit.as_view(),
        name='townplanning_edit'),
)
