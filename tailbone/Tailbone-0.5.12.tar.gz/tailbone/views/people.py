# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2015 Lance Edgar
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
Person Views
"""

from __future__ import unicode_literals, absolute_import

import sqlalchemy as sa

from pyramid.httpexceptions import HTTPFound, HTTPNotFound

from tailbone.views import MasterView, AutocompleteView

from rattail.db import model


class PeopleView(MasterView):
    """
    Master view for the Person class.
    """
    model_class = model.Person
    model_title_plural = "People"
    route_prefix = 'people'

    def configure_grid(self, g):
        g.joiners['email'] = lambda q: q.outerjoin(model.PersonEmailAddress, sa.and_(
            model.PersonEmailAddress.parent_uuid == model.Person.uuid,
            model.PersonEmailAddress.preference == 1))
        g.joiners['phone'] = lambda q: q.outerjoin(model.PersonPhoneNumber, sa.and_(
            model.PersonPhoneNumber.parent_uuid == model.Person.uuid,
            model.PersonPhoneNumber.preference == 1))

        g.filters['email'] = g.make_filter('email', model.PersonEmailAddress.address,
                                           label="Email Address")
        g.filters['phone'] = g.make_filter('phone', model.PersonPhoneNumber.number,
                                           label="Phone Number")

        g.filters['first_name'].default_active = True
        g.filters['first_name'].default_verb = 'contains'

        g.filters['last_name'].default_active = True
        g.filters['last_name'].default_verb = 'contains'

        g.sorters['email'] = lambda q, d: q.order_by(getattr(model.PersonEmailAddress.address, d)())
        g.sorters['phone'] = lambda q, d: q.order_by(getattr(model.PersonPhoneNumber.number, d)())

        g.default_sortkey = 'display_name'

        g.configure(
            include=[
                g.display_name.label("Full Name"),
                g.first_name,
                g.last_name,
                g.phone.label("Phone Number"),
                g.email.label("Email Address"),
            ],
            readonly=True)

    def get_instance(self):
        # TODO: I don't recall why this fallback check for a vendor contact
        # exists here, but leaving it intact for now.
        key = self.request.matchdict['uuid']
        instance = self.Session.query(model.Person).get(key)
        if instance:
            return instance
        instance = self.Session.query(model.VendorContact).get(key)
        if instance:
            return instance.person
        raise HTTPNotFound

    def configure_fieldset(self, fs):
        fs.configure(
            include=[
                fs.display_name.label("Full Name"),
                fs.first_name,
                fs.middle_name,
                fs.last_name,
                fs.phone.label("Phone Number").readonly(),
                fs.email.label("Email Address").readonly(),
                fs.address.label("Mailing Address").readonly(),
            ])


class PeopleAutocomplete(AutocompleteView):

    mapped_class = model.Person
    fieldname = 'display_name'


class PeopleEmployeesAutocomplete(PeopleAutocomplete):
    """
    Autocomplete view for the Person model, but restricted to return only
    results for people who are employees.
    """

    def filter_query(self, q):
        return q.join(model.Employee)


def includeme(config):
    PeopleView.defaults(config)

    # autocomplete
    config.add_route('people.autocomplete', '/people/autocomplete')
    config.add_view(PeopleAutocomplete, route_name='people.autocomplete',
                    renderer='json', permission='people.list')
    config.add_route('people.autocomplete.employees', '/people/autocomplete/employees')
    config.add_view(PeopleEmployeesAutocomplete, route_name='people.autocomplete.employees',
                    renderer='json', permission='people.list')
