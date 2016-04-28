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
Views for employee shifts
"""

from __future__ import unicode_literals, absolute_import

import datetime

import humanize

from rattail.db import model

import formalchemy

from tailbone.views import MasterView


class ShiftLengthField(formalchemy.Field):

    def __init__(self, name, **kwargs):
        kwargs.setdefault('value', self.shift_length)
        super(ShiftLengthField, self).__init__(name, **kwargs)

    def shift_length(self, shift):
        if not shift.punch_in or not shift.punch_out:
            return
        if shift.punch_out < shift.punch_in:
            return "??"
        return humanize.naturaldelta(shift.punch_out - shift.punch_in)


class ScheduledShiftsView(MasterView):
    """
    Master view for employee scheduled shifts.
    """
    model_class = model.ScheduledShift
    url_prefix = '/shifts/scheduled'

    def configure_grid(self, g):
        g.default_sortkey = 'start_time'
        g.default_sortdir = 'desc'
        g.configure(
            include=[
                g.employee,
                g.store,
                g.start_time,
                g.end_time,
            ],
            readonly=True)

    def configure_fieldset(self, fs):
        fs.configure(
            include=[
                fs.employee,
                fs.store,
                fs.start_time,
                fs.end_time,
            ])


class WorkedShiftsView(MasterView):
    """
    Master view for employee worked shifts.
    """
    model_class = model.WorkedShift
    url_prefix = '/shifts/worked'

    def configure_grid(self, g):
        g.default_sortkey = 'punch_in'
        g.default_sortdir = 'desc'
        g.append(ShiftLengthField('length'))
        g.configure(
            include=[
                g.employee,
                g.store,
                g.punch_in,
                g.punch_out,
                g.length,
            ],
            readonly=True)

    def configure_fieldset(self, fs):
        fs.append(ShiftLengthField('length'))
        fs.configure(
            include=[
                fs.employee,
                fs.store,
                fs.punch_in,
                fs.punch_out,
                fs.length,
            ])


def includeme(config):
    ScheduledShiftsView.defaults(config)
    WorkedShiftsView.defaults(config)
