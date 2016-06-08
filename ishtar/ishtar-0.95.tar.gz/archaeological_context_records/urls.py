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

from django.conf.urls.defaults import *

from archaeological_context_records import models
from ishtar_common.wizards import check_rights
import views

# be carreful: each check_rights must be relevant with ishtar_menu

# forms
urlpatterns = patterns(
    '',
    # Context records
    url(r'record_search/(?P<step>.+)?$',
        check_rights(['view_contextrecord', 'view_own_contextrecord'])(
            views.record_search_wizard), name='record_search'),
    url(r'record_creation/(?P<step>.+)?$',
        check_rights(['add_contextrecord'])(
            views.record_creation_wizard), name='record_creation'),
    url(r'record_modification/(?P<step>.+)?$',
        check_rights(['change_contextrecord', 'change_own_contextrecord'])(
            views.record_modification_wizard), name='record_modification'),
    url(r'record_modify/(?P<pk>.+)/$',
        views.record_modify, name='record_modify'),
    url(r'record_deletion/(?P<step>.+)?$',
        check_rights(['change_contextrecord', 'change_own_contextrecord'])(
            views.record_deletion_wizard), name='record_deletion'),
    url(r'record_source_creation/(?P<step>.+)?$',
        check_rights(['change_contextrecord', 'change_own_contextrecord'])(
            views.record_source_creation_wizard),
        name='record_source_creation'),
    url(r'record_source_modification/(?P<step>.+)?$',
        check_rights(['change_contextrecord', 'change_own_contextrecord'])(
            views.record_source_modification_wizard),
        name='record_source_modification'),
    url(r'record_source_deletion/(?P<step>.+)?$',
        check_rights(['change_contextrecord', 'change_own_contextrecord'])(
            views.record_source_deletion_wizard),
        name='record_source_deletion'),
)

urlpatterns += patterns(
    'archaeological_context_records.views',
    url(r'autocomplete-contextrecord/$', 'autocomplete_contextrecord',
        name='autocomplete-contextrecord'),
    url(r'show-contextrecord(?:/(?P<pk>.+))?/(?P<type>.+)?$',
        'show_contextrecord', name=models.ContextRecord.SHOW_URL),
    url(r'show-historized-contextrecord/(?P<pk>.+)?/(?P<date>.+)?$',
        'show_contextrecord', name='show-historized-contextrecord'),
    url(r'revert-contextrecord/(?P<pk>.+)/(?P<date>.+)$',
        'revert_contextrecord', name='revert-contextrecord'),
    url(r'get-contextrecord/own/(?P<type>.+)?$', 'get_contextrecord',
        name='get-own-contextrecord', kwargs={'force_own': True}),
    url(r'get-contextrecord/(?P<type>.+)?$', 'get_contextrecord',
        name='get-contextrecord'),
    url(r'get-contextrecord-for-ope/own/(?P<type>.+)?$',
        'get_contextrecord_for_ope',
        name='get-own-contextrecord-for-ope', kwargs={'force_own': True}),
    url(r'get-contextrecord-for-ope/(?P<type>.+)?$',
        'get_contextrecord_for_ope',
        name='get-contextrecord-for-ope'),
    url(r'get-contextrecord-full/own/(?P<type>.+)?$',
        'get_contextrecord', name='get-own-contextrecord-full',
        kwargs={'full': True, 'force_own': True}),
    url(r'get-contextrecord-full/(?P<type>.+)?$',
        'get_contextrecord', name='get-contextrecord-full',
        kwargs={'full': True}),
    url(r'show-contextrecordsource(?:/(?P<pk>.+))?/(?P<type>.+)?$',
        'show_contextrecordsource', name=models.ContextRecordSource.SHOW_URL),
    url(r'get-contexrecordsource/(?P<type>.+)?$',
        'get_contextrecordsource', name='get-contextrecordsource'),
    url(r'get-contexrecordsource-full/(?P<type>.+)?$',
        'get_contextrecordsource', name='get-contextrecordsource-full',
        kwargs={'full': True}),
)
