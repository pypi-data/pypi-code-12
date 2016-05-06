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

from rattail import enum
from rattail.db import model, api
from rattail.time import localtime, get_sunday

import formencode as fe
from pyramid_simpleform import Form

from tailbone import forms
from tailbone.db import Session
from tailbone.views import View


class ShiftFilter(fe.Schema):
    allow_extra_fields = True
    filter_extra_fields = True
    store = forms.validators.ValidStore()
    department = forms.validators.ValidDepartment()


class TimeSheetView(View):
    """
    Base view for time sheets.
    """
    model_class = None

    # Set this to False to avoid the default behavior of auto-filtering by
    # current store.
    default_filter_store = True

    def __call__(self):
        date = self.get_date()
        store = None
        department = None
        employees = Session.query(model.Employee)\
                           .filter(model.Employee.status == enum.EMPLOYEE_STATUS_CURRENT)

        form = Form(self.request, schema=ShiftFilter)
        if form.validate():
            store = form.data['store']
            department = form.data['department']

        elif self.request.method != 'POST' and self.default_filter_store:
            store = self.rattail_config.get('rattail', 'store')
            if store:
                store = api.get_store(Session(), store)

        # TODO:
        # store = Session.query(model.Store).filter_by(id='003').one()
        # department = Session.query(model.Department).filter_by(number=6).one()

        if store:
            employees = employees.join(model.EmployeeStore)\
                                 .filter(model.EmployeeStore.store == store)

        if department:
            employees = employees.join(model.EmployeeDepartment)\
                                 .filter(model.EmployeeDepartment.department == department)

        return self.render(date, employees.all(), store=store, department=department, form=form)

    def get_date(self):
        date = None
        if 'date' in self.request.params:
            try:
                date = datetime.datetime.strptime(self.request.params['date'], '%Y-%m-%d').date()
            except ValueError:
                self.request.session.flash("The specified date is not valid: {}".format(self.request.params['date']), 'error')
        if not date:
            date = localtime(self.rattail_config).date()
        return date

    def get_stores(self):
        return Session.query(model.Store).order_by(model.Store.id).all()

    def get_store_options(self, stores):
        options = [(s.uuid, "{} - {}".format(s.id, s.name)) for s in stores]
        options.insert(0, (None, "(all)"))
        return options

    def get_departments(self):
        return Session.query(model.Department).order_by(model.Department.name).all()

    def get_department_options(self, departments):
        options = [(d.uuid, d.name) for d in departments]
        options.insert(0, (None, "(all)"))
        return options

    def render(self, date, employees, store=None, department=None, form=None):
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

        stores = self.get_stores()
        store_options = self.get_store_options(stores)

        departments = self.get_departments()
        department_options = self.get_department_options(departments)

        return {
            'form': forms.FormRenderer(form) if form else None,
            'employees': employees,
            'stores': stores,
            'store_options': store_options,
            'store': store,
            'departments': departments,
            'department_options': department_options,
            'department': department,
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
