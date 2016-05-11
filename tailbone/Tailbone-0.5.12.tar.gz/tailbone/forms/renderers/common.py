# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2016 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Common Field Renderers
"""

from __future__ import unicode_literals, absolute_import

import datetime

import pytz

from rattail.time import localtime

import formalchemy
from formalchemy import helpers
from formalchemy.fields import FieldRenderer, SelectFieldRenderer, CheckBoxFieldRenderer
from pyramid.renderers import render

from tailbone.util import pretty_datetime, raw_datetime


class AutocompleteFieldRenderer(FieldRenderer):
    """
    Custom renderer for an autocomplete field.
    """

    service_route = None
    width = '300px'

    @property
    def focus_name(self):
        return self.name + '-textbox'

    @property
    def needs_focus(self):
        return not bool(self.value or self.field_value)

    @property
    def field_display(self):
        return self.raw_value

    @property
    def field_value(self):
        return self.value

    @property
    def service_url(self):
        return self.request.route_url(self.service_route)

    def render(self, **kwargs):
        kwargs.setdefault('field_name', self.name)
        kwargs.setdefault('field_value', self.field_value)
        kwargs.setdefault('field_display', self.field_display)
        kwargs.setdefault('service_url', self.service_url)
        kwargs.setdefault('width', self.width)
        return render('/forms/field_autocomplete.mako', kwargs)

    def render_readonly(self, **kwargs):
        value = self.field_display
        if value is None:
            return u''
        return unicode(value)


class DateTimeFieldRenderer(formalchemy.DateTimeFieldRenderer):
    """
    This renderer assumes the datetime field value is in UTC, and will convert
    it to the local time zone before rendering it in the standard "raw" format.
    """

    def render_readonly(self, **kwargs):
        value = self.raw_value
        if not value:
            return ''
        return raw_datetime(self.request.rattail_config, value)


class DateTimePrettyFieldRenderer(formalchemy.DateTimeFieldRenderer):
    """
    Custom date/time field renderer, which displays a "pretty" value in
    read-only mode, leveraging config to show the correct timezone.
    """

    def render_readonly(self, **kwargs):
        value = self.raw_value
        if not value:
            return ''
        return pretty_datetime(self.request.rattail_config, value)


class TimeFieldRenderer(formalchemy.TimeFieldRenderer):
    """
    Custom renderer for time fields.  In edit mode, renders a simple text
    input, which is expected to become a 'timepicker' widget in the UI.
    However the particular magic required for that lives in 'tailbone.js'.
    """
    format = '%I:%M %p'

    def render(self, **kwargs):
        kwargs.setdefault('class_', 'timepicker')
        return helpers.text_field(self.name, value=self.value, **kwargs)

    def render_readonly(self, **kwargs):
        return self.render_value(self.raw_value)

    def render_value(self, value):
        value = self.convert_value(value)
        if isinstance(value, datetime.time):
            return value.strftime(self.format)
        return ''

    def convert_value(self, value):
        if isinstance(value, datetime.datetime):
            if not value.tzinfo:
                value = pytz.utc.localize(value)
            return localtime(self.request.rattail_config, value).time()
        return value

    def stringify_value(self, value, as_html=False):
        if not as_html:
            return self.render_value(value)
        return super(TimeFieldRenderer, self).stringify_value(value, as_html=as_html)

    def _serialized_value(self):
        return self.params.getone(self.name)

    def deserialize(self):
        value = self._serialized_value()
        if value:
            try:
                return datetime.datetime.strptime(value, self.format).time()
            except ValueError:
                pass


class EnumFieldRenderer(SelectFieldRenderer):
    """
    Renderer for simple enumeration fields.
    """
    enumeration = {}
    render_key = False

    def __init__(self, arg, render_key=False):
        if isinstance(arg, dict):
            self.enumeration = arg
            self.render_key = render_key
        else:
            self(arg)

    def __call__(self, field):
        super(EnumFieldRenderer, self).__init__(field)
        return self

    def render_readonly(self, **kwargs):
        value = self.raw_value
        if value is None:
            return ''
        rendered = self.enumeration.get(value, unicode(value))
        if self.render_key:
            rendered = '{} - {}'.format(value, rendered)
        return rendered

    def render(self, **kwargs):
        opts = [(self.enumeration[x], x) for x in self.enumeration]
        return SelectFieldRenderer.render(self, opts, **kwargs)


class DecimalFieldRenderer(formalchemy.FieldRenderer):
    """
    Sort of generic field renderer for decimal values.  You must provide the
    number of places after the decimal (scale).  Note that this in turn relies
    on simple string formatting; the renderer does not attempt any mathematics
    of its own.
    """

    def __init__(self, scale):
        self.scale = scale

    def __call__(self, field):
        super(DecimalFieldRenderer, self).__init__(field)
        return self

    def render_readonly(self, **kwargs):
        value = self.raw_value
        if value is None:
            return ''
        fmt = '{{0:0.{0}f}}'.format(self.scale)
        return fmt.format(value)


class CurrencyFieldRenderer(formalchemy.FieldRenderer):
    """
    Sort of generic field renderer for currency values.
    """

    def render_readonly(self, **kwargs):
        value = self.raw_value
        if value is None:
            return ''
        if value < 0:
            return "(${:0,.2f})".format(0 - value)
        return "${:0,.2f}".format(value)


class YesNoFieldRenderer(CheckBoxFieldRenderer):

    def render_readonly(self, **kwargs):
        value = self.raw_value
        if value is None:
            return u''
        return u'Yes' if value else u'No'
