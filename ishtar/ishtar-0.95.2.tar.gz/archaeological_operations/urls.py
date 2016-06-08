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
import models

# be carreful: each check_rights must be relevant with ishtar_menu

# forms
urlpatterns = patterns(
    '',
    url(r'operation_administrativeactop_search/(?P<step>.+)?$',
        check_rights(['change_administrativeact'])(
            views.operation_administrativeactop_search_wizard),
        name='operation_administrativeactop_search'),
    url(r'operation_administrativeactop/(?P<step>.+)?$',
        check_rights(['change_administrativeact'])(
            views.operation_administrativeactop_wizard),
        name='operation_administrativeactop'),
    url(r'operation_administrativeactop_modification/(?P<step>.+)?$',
        check_rights(['change_administrativeact'])(
            views.operation_administrativeactop_modification_wizard),
        name='operation_administrativeactop_modification'),
    url(r'operation_administrativeactop_deletion/(?P<step>.+)?$',
        check_rights(['change_administrativeact'])(
            views.operation_administrativeactop_deletion_wizard),
        name='operation_administrativeactop_deletion'),
    url(r'operation_source_search/(?P<step>.+)?$',
        check_rights(['view_operation', 'view_own_operation'])(
            views.operation_source_search_wizard),
        name='operation_source_search'),
    url(r'operation_source_creation/(?P<step>.+)?$',
        check_rights(['change_operation', 'change_own_operation'])(
            views.operation_source_creation_wizard),
        name='operation_source_creation'),
    url(r'operation_source_modification/(?P<step>.+)?$',
        check_rights(['change_operation', 'change_own_operation'])(
            views.operation_source_modification_wizard),
        name='operation_source_modification'),
    url(r'operation_source_deletion/(?P<step>.+)?$',
        check_rights(['change_operation', 'change_own_operation'])(
            views.operation_source_deletion_wizard),
        name='operation_source_deletion'),
    url(r'operation_search/(?P<step>.+)?$',
        check_rights(['view_operation', 'view_own_operation'])(
            views.operation_search_wizard), name='operation_search'),
    url(r'operation_creation/(?P<step>.+)?$',
        check_rights(['add_operation'])(views.operation_creation_wizard),
        name='operation_creation'),
    url(r'operation_add/(?P<file_id>\d+)$',
        views.operation_add, name='operation_add'),
    url(r'operation_modification/(?P<step>.+)?$',
        check_rights(['change_operation', 'change_own_operation'])(
            views.operation_modification_wizard),
        name='operation_modification'),
    url(r'operation_modify/(?P<pk>.+)/$',
        views.operation_modify, name='operation_modify'),
    url(r'operation_closing/(?P<step>.+)?$',
        check_rights(['change_operation'])(
            views.operation_closing_wizard), name='operation_closing'),
    url(r'operation_deletion/(?P<step>.+)?$',
        check_rights(['change_operation', 'change_own_operation'])(
            views.operation_deletion_wizard), name='operation_deletion'),
    url(r'administrativact_register/(?P<step>.+)?$',
        check_rights(['view_administrativeact', 'view_own_administrativeact'])(
            views.administrativact_register_wizard),
        name='administrativact_register'),
)

urlpatterns += patterns(
    'archaeological_operations.views',
    url(r'autocomplete-operation/$', 'autocomplete_operation',
        name='autocomplete-operation'),
    url(r'get-operation/own/(?P<type>.+)?$',
        'get_operation', name='get-own-operation',
        kwargs={'force_own': True}),
    url(r'get-operation/(?P<type>.+)?$', 'get_operation',
        name='get-operation'),
    url(r'get-operation-full/(?P<type>.+)?$', 'get_operation',
        name='get-operation-full', kwargs={'full': True}),
    url(r'get-operation-full/own/(?P<type>.+)?$',
        'get_operation', name='get-own-operation-full',
        kwargs={'full': True, 'force_own': True}),
    url(r'get-available-operation-code/(?P<year>.+)?$',
        'get_available_operation_code', name='get_available_operation_code'),
    url(r'revert-operation/(?P<pk>.+)/(?P<date>.+)$',
        'revert_operation', name='revert-operation'),
    url(r'show-operation(?:/(?P<pk>.+))?/(?P<type>.+)?$',
        'show_operation', name=models.Operation.SHOW_URL),
    url(r'show-historized-operation/(?P<pk>.+)?/(?P<date>.+)?$',
        'show_operation', name='show-historized-operation'),
    url(r'get-administrativeactop/(?P<type>.+)?$',
        'get_administrativeactop', name='get-administrativeactop'),
    url(r'get-administrativeact/(?P<type>.+)?$',
        'get_administrativeact', name='get-administrativeact'),
    url(r'get-administrativeact-full/(?P<type>.+)?$',
        'get_administrativeact', name='get-administrativeact-full',
        kwargs={'full': True}),
    url(r'show-administrativeact(?:/(?P<pk>.+))?/(?P<type>.+)?$',
        'show_administrativeact', name='show-administrativeact'),
    # allow specialization for operations
    url(r'show-administrativeact(?:/(?P<pk>.+))?/(?P<type>.+)?$',
        'show_administrativeact', name='show-administrativeactop'),
    # allow specialization for files
    url(r'show-administrativeact(?:/(?P<pk>.+))?/(?P<type>.+)?$',
        'show_administrativeact', name='show-administrativeactfile'),
    url(r'generatedoc-administrativeactop/(?P<pk>.+)?/(?P<template_pk>.+)?$',
        'generatedoc_administrativeactop',
        name='generatedoc-administrativeactop'),
    url(r'show-operationsource(?:/(?P<pk>.+))?/(?P<type>.+)?$',
        'show_operationsource', name=models.OperationSource.SHOW_URL),
    url(r'get-operationsource/(?P<type>.+)?$',
        'get_operationsource', name='get-operationsource'),
    url(r'get-operationsource-full/(?P<type>.+)?$',
        'get_operationsource', name='get-operationsource-full',
        kwargs={'full': True}),
    url(r'dashboard_operation/$', 'dashboard_operation',
        name='dashboard-operation'),
    url(r'autocomplete-archaeologicalsite/$',
        'autocomplete_archaeologicalsite',
        name='autocomplete-archaeologicalsite'),
    url(r'new-archaeologicalsite/(?:(?P<parent_name>[^/]+)/)?'
        r'(?:(?P<limits>[^/]+)/)?$',
        'new_archaeologicalsite', name='new-archaeologicalsite'),
    url(r'autocomplete-patriarche/$', 'autocomplete_patriarche',
        name='autocomplete-patriarche'),
    url(r'operation_administrativeact_document/$',
        'administrativeactfile_document',
        name='operation-administrativeact-document'),
)
