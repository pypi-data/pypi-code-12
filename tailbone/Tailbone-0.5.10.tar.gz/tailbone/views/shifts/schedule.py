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
Views for employee schedules
"""

from __future__ import unicode_literals, absolute_import

from rattail import enum
from rattail.db import model

from tailbone.db import Session
from tailbone.views.shifts.lib import TimeSheetView


class ScheduleView(TimeSheetView):
    """
    Simple view for current user's schedule.
    """
    model_class = model.ScheduledShift

    def __call__(self):
        date = self.get_date()
        employees = Session.query(model.Employee)\
                           .filter(model.Employee.status == enum.EMPLOYEE_STATUS_CURRENT)

        # TODO:
        # store = Session.query(model.Store).filter_by(id='003').one()
        # department = Session.query(model.Department).filter_by(number=6).one()

        # if store:
        #     employees = employees.join(model.EmployeeStore)\
        #                          .filter(model.EmployeeStore.store == store)
        # if department:
        #     employees = employees.join(model.EmployeeDepartment)\
        #                          .filter(model.EmployeeDepartment.department == department)

        return self.render(date, employees.all())


def includeme(config):

    config.add_tailbone_permission('schedule', 'schedule.view', "View Schedule")

    # current user's schedule
    config.add_route('schedule', '/schedule/')
    config.add_view(ScheduleView, route_name='schedule',
                    renderer='/shifts/schedule.mako', permission='schedule.view')
