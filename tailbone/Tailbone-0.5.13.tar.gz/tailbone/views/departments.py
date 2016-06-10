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
Department Views
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model

from tailbone.views import MasterView, AutocompleteView, AlchemyGridView
from tailbone.views.continuum import VersionView, version_defaults
from tailbone.newgrids import AlchemyGrid, GridAction


class DepartmentsView(MasterView):
    """
    Master view for the Department class.
    """
    model_class = model.Department

    def configure_grid(self, g):
        g.filters['name'].default_active = True
        g.filters['name'].default_verb = 'contains'
        g.default_sortkey = 'number'
        g.configure(
            include=[
                g.number,
                g.name,
            ],
            readonly=True)

    def configure_fieldset(self, fs):
        fs.configure(
            include=[
                fs.number,
                fs.name,
            ])
        return fs

    def template_kwargs_view(self, **kwargs):
        department = kwargs['instance']
        if department.employees:

            # TODO: This is the second attempt (after role.users) at using a
            # new grid outside of the context of a primary master grid.  The
            # API here is really much hairier than I'd like...  Looks like we
            # shouldn't need a key for this one, for instance (no settings
            # required), but there is plenty of room for improvement here.
            employees = sorted(department.employees, key=unicode)
            employees = AlchemyGrid('departments.employees', self.request, data=employees, model_class=model.Employee,
                                      main_actions=[
                                          GridAction('view', icon='zoomin',
                                                     url=lambda r, i: self.request.route_url('employees.view', uuid=r.uuid)),
                                      ])
            employees.configure(include=[employees.display_name], readonly=True)
            kwargs['employees'] = employees

        else:
            kwargs['employees'] = None
        return kwargs


class DepartmentVersionView(VersionView):
    """
    View which shows version history for a department.
    """
    parent_class = model.Department
    route_model_view = 'departments.view'


class DepartmentsByVendorGrid(AlchemyGridView):

    mapped_class = model.Department
    config_prefix = 'departments.by_vendor'
    checkboxes = True
    partial_only = True

    def query(self):
        return self.make_query()\
            .outerjoin(model.Product)\
            .join(model.ProductCost)\
            .join(model.Vendor)\
            .filter(model.Vendor.uuid == self.request.params['uuid'])\
            .distinct()\
            .order_by(model.Department.name)

    def grid(self):
        g = self.make_grid()
        g.configure(
            include=[
                g.name,
                ],
            readonly=True)
        return g


class DepartmentsAutocomplete(AutocompleteView):

    mapped_class = model.Department
    fieldname = 'name'


def includeme(config):

    # autocomplete
    config.add_route('departments.autocomplete',        '/departments/autocomplete')
    config.add_view(DepartmentsAutocomplete, route_name='departments.autocomplete',
                    renderer='json', permission='departments.list')

    # departments by vendor list
    config.add_route('departments.by_vendor',           '/departments/by-vendor')
    config.add_view(DepartmentsByVendorGrid,route_name='departments.by_vendor',
                    permission='departments.list')

    DepartmentsView.defaults(config)
    version_defaults(config, DepartmentVersionView, 'department')
