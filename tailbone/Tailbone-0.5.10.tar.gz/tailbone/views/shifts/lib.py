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
Base views for time sheets
"""

from __future__ import unicode_literals, absolute_import

import datetime

from rattail.db import model
from rattail.time import localtime, get_sunday

from tailbone.db import Session
from tailbone.views import View


class TimeSheetView(View):
    """
    Base view for time sheets.
    """
    model_class = None

    def get_date(self):
        date = None
        if 'date' in self.request.GET:
            try:
                date = datetime.datetime.strptime(self.request.GET['date'], '%Y-%m-%d').date()
            except ValueError:
                self.request.session.flash("The specified date is not valid: {}".format(self.request.GET['date']), 'error')
        if not date:
            date = localtime(self.rattail_config).date()
        return date

    def render(self, date, employees):
        """
        Render a time sheet for one or more employees, for the week which
        includes the specified date.
        """
        sunday = get_sunday(date)
        weekdays = [sunday]
        for i in range(1, 7):
            weekdays.append(sunday + datetime.timedelta(days=i))

        saturday = weekdays[-1]
        if saturday.year == sunday.year:
            week_of = '{} - {}'.format(sunday.strftime('%a %b %d'), saturday.strftime('%a %b %d, %Y'))
        else:
            week_of = '{} - {}'.format(sunday.strftime('%a %b %d, Y'), saturday.strftime('%a %b %d, %Y'))

        self.modify_employees(employees, weekdays)
        return {
            'employees': employees,
            'week_of': week_of,
            'sunday': sunday,
            'prev_sunday': sunday - datetime.timedelta(days=7),
            'next_sunday': sunday + datetime.timedelta(days=7),
            'weekdays': weekdays,
        }

    def modify_employees(self, employees, weekdays):
        min_time = localtime(self.rattail_config, datetime.datetime.combine(weekdays[0], datetime.time(0)))
        max_time = localtime(self.rattail_config, datetime.datetime.combine(weekdays[-1] + datetime.timedelta(days=1), datetime.time(0)))
        shifts = Session.query(self.model_class)\
                        .filter(self.model_class.employee_uuid.in_([e.uuid for e in employees]))\
                        .filter(self.model_class.start_time >= min_time)\
                        .filter(self.model_class.start_time < max_time)\
                        .all()

        for employee in employees:
            employee_shifts = sorted([s for s in shifts if s.employee_uuid == employee.uuid],
                                     key=lambda s: (s.start_time, s.end_time))
            employee.weekdays = []
            employee.hours = datetime.timedelta(0)
            employee.hours_display = '0'

            for day in weekdays:
                empday = {
                    'shifts': [],
                    'hours': datetime.timedelta(0),
                    'hours_display': '',
                }

                while employee_shifts:
                    shift = employee_shifts[0]
                    if shift.employee_uuid != employee.uuid:
                        break
                    elif shift.get_date(self.rattail_config) == day:
                        empday['shifts'].append(shift)
                        empday['hours'] += shift.length
                        employee.hours += shift.length
                        del employee_shifts[0]
                    else:
                        break

                if empday['hours']:
                    minutes = (empday['hours'].days * 1440) + (empday['hours'].seconds / 60)
                    empday['hours_display'] = '{}:{:02d}'.format(minutes // 60, minutes % 60)
                employee.weekdays.append(empday)

            if employee.hours:
                minutes = (employee.hours.days * 1440) + (employee.hours.seconds / 60)
                employee.hours_display = '{}:{:02d}'.format(minutes // 60, minutes % 60)
