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

from django.conf.urls.defaults import *

from ishtar_common.wizards import check_rights
import views

# be carreful: each check_rights must be relevant with ishtar_menu

# forms:
urlpatterns = patterns(
    '',
    url(r'file_administrativeactfil_search/(?P<step>.+)?$',
        check_rights(['change_administrativeact'])(
            views.file_administrativeactfile_search_wizard),
        name='file_administrativeactfile_search'),
    url(r'file_administrativeactfil/(?P<step>.+)?$',
        check_rights(['change_administrativeact'])(
            views.file_administrativeactfile_wizard),
        name='file_administrativeactfile'),
    url(r'file_administrativeactfil_deletion/(?P<step>.+)?$',
        check_rights(['change_administrativeact'])(
            views.file_administrativeactfile_deletion_wizard),
        name='file_administrativeactfile_deletion'),
    url(r'file_administrativeactfil_modification/(?P<step>.+)?$',
        check_rights(['change_administrativeact'])(
            views.file_administrativeactfile_modification_wizard),
        name='file_administrativeactfile_modification'),
    url(r'file_search/(?P<step>.+)?$',
        check_rights(['view_file', 'view_own_file'])(
            views.file_search_wizard),
        name='file_search'),
    url(r'file_creation/(?P<step>.+)?$',
        check_rights(['add_file'])(
            views.file_creation_wizard), name='file_creation'),
    url(r'file_modification/(?P<step>.+)?$',
        check_rights(['change_file', 'change_own_file'])(
            views.file_modification_wizard), name='file_modification'),
    url(r'file_modify/(?P<pk>.+)/$', views.file_modify, name='file_modify'),
    url(r'file_closing/(?P<step>.+)?$',
        check_rights(['change_file'])(
            views.file_closing_wizard),
        name='file_closing'),
    url(r'file_deletion/(?P<step>.+)?$',
        check_rights(['delete_file', 'delete_own_file'])(
            views.file_deletion_wizard),
        name='file_deletion'),
)

urlpatterns += patterns(
    'archaeological_files.views',
    url(r'autocomplete-file/$', 'autocomplete_file',
        name='autocomplete-file'),
    url(r'get-file/(?P<type>.+)?$', 'get_file',
        name='get-file'),
    url(r'get-file-full/(?P<type>.+)?$', 'get_file',
        name='get-file-full', kwargs={'full': True}),
    url(r'get-administrativeactfile/(?P<type>.+)?$',
        'get_administrativeactfile', name='get-administrativeactfile'),
    url(r'show-file(?:/(?P<pk>.+))?/(?P<type>.+)?$', 'show_file',
        name='show-file'),
    url(r'show-historized-file/(?P<pk>.+)?/(?P<date>.+)?$',
        'show_file', name='show-historized-file'),
    url(r'revert-file/(?P<pk>.+)/(?P<date>.+)$',
        'revert_file', name='revert-file'),
    url(r'dashboard_file/$', 'dashboard_file', name='dashboard-file'),
)

urlpatterns += patterns(
    'archaeological_operations.views',
    url(r'file_administrativeact_document/$',
        'administrativeactfile_document',
        name='file-administrativeact-document', kwargs={'operation': False}),
)
