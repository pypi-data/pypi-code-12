#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2013 Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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

from django.forms import widgets
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


class ParcelWidget(widgets.MultiWidget):
    def __init__(self, attrs=None):
        if not attrs:
            attrs = {'class': 'widget-parcel'}
        elif 'class' not in attrs:
            attrs['class'] = 'widget-parcel'
        else:
            attrs['class'] += ' widget-parcel'
        _widgets = (
            widgets.TextInput(attrs=attrs),
            widgets.TextInput(attrs=attrs),
        )
        super(ParcelWidget, self).__init__(_widgets, attrs)

    def decompress(self, value):
        if value:
            return value
        return [None, None]

    def format_output(self, rendered_widgets):
        return u' / '.join(rendered_widgets)


class SelectParcelWidget(widgets.TextInput):
    def render(self, *args, **kwargs):
        render = super(SelectParcelWidget, self).render(*args, **kwargs)
        render += u" <button name='formset_add' value='add'>%s</button>" \
            % _(u"Add")
        return mark_safe(render)
