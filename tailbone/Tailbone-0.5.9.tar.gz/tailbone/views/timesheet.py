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
Views for employee time sheets
"""

from __future__ import unicode_literals, absolute_import

import datetime

from rattail.db import model
from rattail.time import localtime, get_sunday

from tailbone.db import Session
from tailbone.views import View


class TimeSheetView(View):
    """
    Simple view for current user's time sheet.
    """

    def __call__(self):
        employee = self.request.user.employee
        assert employee
        today = localtime(self.rattail_config).date()
        sunday = get_sunday(today)

        weekdays = [sunday]
        for i in range(1, 7):
            weekdays.append(sunday + datetime.timedelta(days=i))

        saturday = weekdays[-1]
        if saturday.year == sunday.year:
            week_of = '{} - {}'.format(sunday.strftime('%a %b %d'), saturday.strftime('%a %b %d, %Y'))
        else:
            week_of = '{} - {}'.format(sunday.strftime('%a %b %d, Y'), saturday.strftime('%a %b %d, %Y'))

        min_punch = localtime(self.rattail_config, datetime.datetime.combine(sunday, datetime.time(0)))
        max_punch = localtime(self.rattail_config, datetime.datetime.combine(saturday + datetime.timedelta(days=1), datetime.time(0)))
        shifts = Session.query(model.WorkedShift)\
                        .filter(model.WorkedShift.employee == employee)\
                        .filter(model.WorkedShift.punch_in >= min_punch)\
                        .filter(model.WorkedShift.punch_in < max_punch)\
                        .order_by(model.WorkedShift.punch_in, model.WorkedShift.punch_out)\
                        .all()

        shifts_copy = list(shifts)
        employee.weekdays = []
        employee.hours = datetime.timedelta(0)
        for day in weekdays:
            empday = {'shifts': [], 'hours': datetime.timedelta(0)}

            while shifts_copy:
                shift = shifts_copy[0]
                if shift.get_date(self.rattail_config) == day:
                    empday['shifts'].append(shift)
                    empday['hours'] += shift.length
                    employee.hours += shift.length
                    del shifts_copy[0]
                else:
                    break

            empday['hours_display'] = '0'
            if empday['hours']:
                minutes = (empday['hours'].days * 1440) + (empday['hours'].seconds / 60)
                empday['hours_display'] = '{}:{:02d}'.format(minutes // 60, minutes % 60)
            employee.weekdays.append(empday)

        employee.hours_display = '0'
        if employee.hours:
            minutes = (employee.hours.days * 1440) + (employee.hours.seconds / 60)
            employee.hours_display = '{}:{:02d}'.format(minutes // 60, minutes % 60)

        return {
            'employee': employee,
            'week_of': week_of,
            'sunday': sunday,
            'weekdays': weekdays,
            'shifts': shifts,
        }


def includeme(config):

    # current user's time sheet
    config.add_route('timesheet', '/timesheet/')
    config.add_view(TimeSheetView, route_name='timesheet',
                    renderer='/timesheet/index.mako',
                    permission='timesheet.view')
    config.add_tailbone_permission('timesheet', 'timesheet.view', "View Time Sheet")
