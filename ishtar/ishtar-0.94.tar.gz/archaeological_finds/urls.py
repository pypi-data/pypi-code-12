#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2010-2016 Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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

from archaeological_finds import models

# be carreful: each check_rights must be relevant with ishtar_menu

# forms
urlpatterns = patterns(
    '',
    url(r'find_search/(?P<step>.+)?$',
        check_rights(['view_find', 'view_own_find'])(
            views.find_search_wizard), name='find_search'),
    url(r'find_creation/(?P<step>.+)?$',
        check_rights(['add_find'])(
            views.find_creation_wizard), name='find_creation'),
    url(r'find_modification/(?P<step>.+)?$',
        check_rights(['change_find', 'change_own_find'])(
            views.find_modification_wizard), name='find_modification'),
    url(r'find_deletion/(?P<step>.+)?$',
        check_rights(['change_find', 'change_own_find'])(
            views.find_deletion_wizard), name='find_deletion'),
    url(r'find_modify/(?P<pk>.+)/$',
        views.find_modify, name='find_modify'),
    url(r'find_source_creation/(?P<step>.+)?$',
        check_rights(['change_find', 'change_own_find'])(
            views.find_source_creation_wizard),
        name='find_source_creation'),
    url(r'find_source_modification/(?P<step>.+)?$',
        check_rights(['change_find', 'change_own_find'])(
            views.find_source_modification_wizard),
        name='find_source_modification'),
    url(r'find_source_deletion/(?P<step>.+)?$',
        check_rights(['change_find', 'change_own_find'])(
            views.find_source_deletion_wizard),
        name='find_source_deletion'),
    url(r'^find_basket_creation/$',
        check_rights(['change_find', 'change_own_find'])(
            views.NewFindBasketView.as_view()), name='new_findbasket'),
    url(r'^find_basket_modification_add/$',
        check_rights(['change_find', 'change_own_find'])(
            views.SelectBasketForManagement.as_view()),
        name='select_findbasketforadd'),
    url(r'^find_basket_modification_add/(?P<pk>[0-9]+)?/$',
        check_rights(['change_find', 'change_own_find'])(
            views.SelectItemsInBasket.as_view()),
        name='select_itemsinbasket'),
    url(r'^find_basket_modification_add_item/$',
        check_rights(['change_find', 'change_own_find'])(
            views.FindBasketAddItemView.as_view()),
        name='add_iteminbasket'),
    url(r'^find_basket_modification_delete_item/(?P<basket>[0-9]+)?'
        r'/(?P<find_pk>[0-9]+)?/$',
        check_rights(['change_find', 'change_own_find'])(
            views.FindBasketDeleteItemView.as_view()),
        name='delete_iteminbasket'),
    url(r'^find_basket_list/(?P<pk>[0-9]+)?/$',
        check_rights(['change_find', 'change_own_find'])(
            views.FindBasketListView.as_view()),
        name='list_iteminbasket'),
    url(r'^find_basket_deletion/$',
        check_rights(['change_find', 'change_own_find'])(
            views.DeleteFindBasketView.as_view()), name='delete_findbasket'),
)

urlpatterns += patterns(
    'archaeological_finds.views',
    url(r'autocomplete-objecttype/$', 'autocomplete_objecttype',
        name='autocomplete-objecttype'),
    url(r'autocomplete-materialtype/$', 'autocomplete_materialtype',
        name='autocomplete-materialtype'),
    url(r'autocomplete-preservationtype/$', 'autocomplete_preservationtype',
        name='autocomplete-preservationtype'),
    url(r'autocomplete-integritytype/$', 'autocomplete_integritytype',
        name='autocomplete-integritytype'),
    url(r'get-find/own/(?P<type>.+)?$', 'get_find',
        name='get-own-find', kwargs={'force_own': True}),
    url(r'get-find/(?P<type>.+)?$', 'get_find',
        name='get-find'),
    url(r'get-find-for-ope/own/(?P<type>.+)?$', 'get_find_for_ope',
        name='get-own-find-for-ope', kwargs={'force_own': True}),
    url(r'get-find-for-ope/(?P<type>.+)?$', 'get_find_for_ope',
        name='get-find-for-ope'),
    url(r'get-find-full/own/(?P<type>.+)?$', 'get_find',
        name='get-own-find-full', kwargs={'full': True, 'force_own': True}),
    url(r'get-find-full/(?P<type>.+)?$', 'get_find',
        name='get-find-full', kwargs={'full': True}),
    url(r'get-findsource/(?P<type>.+)?$',
        'get_findsource', name='get-findsource'),
    url(r'get-findsource-full/(?P<type>.+)?$',
        'get_findsource', name='get-findsource-full',
        kwargs={'full': True}),
    url(r'show-findsource(?:/(?P<pk>.+))?/(?P<type>.+)?$', 'show_findsource',
        name=models.FindSource.SHOW_URL),
    url(r'show-find/basket-(?P<pk>.+)/(?P<type>.+)?$', 'show_findbasket',
        name='show-findbasket'),
    url(r'show-find(?:/(?P<pk>.+))?/(?P<type>.+)?$', 'show_find',
        name=models.Find.SHOW_URL),
    url(r'show-historized-find/(?P<pk>.+)?/(?P<date>.+)?$',
        'show_find', name='show-historized-find'),
    url(r'revert-find/(?P<pk>.+)/(?P<date>.+)$',
        'revert_find', name='revert-find'),
)
