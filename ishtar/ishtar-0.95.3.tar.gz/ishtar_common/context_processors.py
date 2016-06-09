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

from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _

from ishtar_common.utils import shortify

from menus import Menu

from ishtar_common.models import get_current_profile
from archaeological_operations.models import Operation
from archaeological_files.models import File
from archaeological_context_records.models import ContextRecord
from archaeological_finds.models import Find

profile = get_current_profile()
CURRENT_ITEMS = []
if profile.files:
    CURRENT_ITEMS.append((_(u"Archaeological file"), File))
CURRENT_ITEMS.append((_(u"Operation"), Operation))
if profile.context_record:
    CURRENT_ITEMS.append((_(u"Context record"), ContextRecord))
if profile.find:
    CURRENT_ITEMS.append((_(u"Find"), Find))


def get_base_context(request):
    dct = {'URL_PATH': settings.URL_PATH}
    try:
        dct["APP_NAME"] = Site.objects.get_current().name
    except Site.DoesNotExist:
        dct["APP_NAME"] = settings.APP_NAME
    dct["COUNTRY"] = settings.COUNTRY
    """
    if 'MENU' not in request.session or \
       request.session['MENU'].user != request.user:
        menu = Menu(request.user)
        menu.init()
        request.session['MENU'] = menu
    """  # temporary disabled
    current_action = None
    if 'CURRENT_ACTION' in request.session:
        dct['CURRENT_ACTION'] = request.session['CURRENT_ACTION']
        current_action = dct['CURRENT_ACTION']
    menu = Menu(request.user, current_action=current_action,
                session=request.session)
    menu.init()
    if menu.selected_idx is not None:
        dct['current_theme'] = "theme-%d" % (menu.selected_idx + 1)
    request.session['MENU'] = menu
    dct['MENU'] = request.session['MENU']
    dct['JQUERY_URL'] = settings.JQUERY_URL
    dct['JQUERY_UI_URL'] = settings.JQUERY_UI_URL
    dct['COUNTRY'] = settings.COUNTRY
    dct['current_menu'] = []
    for lbl, model in CURRENT_ITEMS:
        model_name = model.__name__.lower()
        cls = ''
        current = model_name in request.session and request.session[model_name]
        items = []
        for item in model.get_owns(request.user):
            pk = unicode(item.pk)
            if item.IS_BASKET:
                pk = "basket-" + pk
            selected = pk == current
            if selected:
                cls = item.get_short_menu_class()
            items.append((pk, shortify(unicode(item), 60),
                          selected, item.get_short_menu_class()))
        if items:
            dct['current_menu'].append((lbl, model_name, cls, items))
    return dct
