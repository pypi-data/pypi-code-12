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
Customer Views
"""

from __future__ import unicode_literals, absolute_import

import re

import sqlalchemy as sa
from sqlalchemy import orm

from pyramid.httpexceptions import HTTPNotFound

from tailbone import forms
from tailbone.db import Session
from tailbone.views import MasterView, AutocompleteView

from rattail import enum
from rattail.db import model


class CustomersView(MasterView):
    """
    Master view for the Customer class.
    """
    model_class = model.Customer

    def configure_grid(self, g):

        g.joiners['email'] = lambda q: q.outerjoin(model.CustomerEmailAddress, sa.and_(
            model.CustomerEmailAddress.parent_uuid == model.Customer.uuid,
            model.CustomerEmailAddress.preference == 1))
        g.joiners['phone'] = lambda q: q.outerjoin(model.CustomerPhoneNumber, sa.and_(
            model.CustomerPhoneNumber.parent_uuid == model.Customer.uuid,
            model.CustomerPhoneNumber.preference == 1))

        g.filters['email'] = g.make_filter('email', model.CustomerEmailAddress.address,
                                           label="Email Address")
        g.filters['phone'] = g.make_filter('phone', model.CustomerPhoneNumber.number,
                                           label="Phone Number")

        # TODO
        # name=self.filter_ilike_and_soundex(model.Customer.name),

        g.filters['name'].default_active = True
        g.filters['name'].default_verb = 'contains'
        g.filters['id'].label = "ID"

        g.sorters['email'] = lambda q, d: q.order_by(getattr(model.CustomerEmailAddress.address, d)())
        g.sorters['phone'] = lambda q, d: q.order_by(getattr(model.CustomerPhoneNumber.number, d)())

        g.default_sortkey = 'name'

        g.configure(
            include=[
                g.id.label("ID"),
                g.name,
                g.phone.label("Phone Number"),
                g.email.label("Email Address"),
            ],
            readonly=True)

    def get_instance(self):
        try:
            instance = super(CustomersView, self).get_instance()
        except HTTPNotFound:
            pass
        else:
            if instance:
                return instance

        key = self.request.matchdict['uuid']

        # search by Customer.id
        instance = self.Session.query(model.Customer)\
                               .filter(model.Customer.id == key)\
                               .first()
        if instance:
            return instance

        # search by CustomerPerson.uuid
        instance = self.Session.query(model.CustomerPerson).get(key)
        if instance:
            return instance.customer

        # search by CustomerGroupAssignment.uuid
        instance = self.Session.query(model.CustomerGroupAssignment).get(key)
        if instance:
            return instance.customer

        raise HTTPNotFound

    def configure_fieldset(self, fs):
        fs.email_preference.set(renderer=forms.EnumFieldRenderer(enum.EMAIL_PREFERENCE))
        fs.configure(
            include=[
                fs.id.label("ID"),
                fs.name,
                fs.phone.label("Phone Number").readonly(),
                fs.email.label("Email Address").readonly(),
                fs.email_preference,
            ])


class CustomerNameAutocomplete(AutocompleteView):
    """
    Autocomplete view which operates on customer name.
    """
    mapped_class = model.Customer
    fieldname = 'name'


class CustomerPhoneAutocomplete(AutocompleteView):
    """
    Autocomplete view which operates on customer phone number.

    .. note::
       As currently implemented, this view will only work with a PostgreSQL
       database.  It normalizes the user's search term and the database values
       to numeric digits only (i.e. removes special characters from each) in
       order to be able to perform smarter matching.  However normalizing the
       database value currently uses the PG SQL ``regexp_replace()`` function.
    """
    invalid_pattern = re.compile(r'\D')

    def prepare_term(self, term):
        return self.invalid_pattern.sub('', term)

    def query(self, term):
        return Session.query(model.CustomerPhoneNumber)\
            .filter(sa.func.regexp_replace(model.CustomerPhoneNumber.number, r'\D', '', 'g').like('%{0}%'.format(term)))\
            .order_by(model.CustomerPhoneNumber.number)\
            .options(orm.joinedload(model.CustomerPhoneNumber.customer))

    def display(self, phone):
        return "{0} {1}".format(phone.number, phone.customer)

    def value(self, phone):
        return phone.customer.uuid


def customer_info(request):
    """
    View which returns simple dictionary of info for a particular customer.
    """
    uuid = request.params.get('uuid')
    customer = Session.query(model.Customer).get(uuid) if uuid else None
    if not customer:
        return {}
    return {
        'uuid':                 customer.uuid,
        'name':                 customer.name,
        'phone_number':         customer.phone.number if customer.phone else '',
        }


def includeme(config):

    # autocomplete
    config.add_route('customers.autocomplete', '/customers/autocomplete')
    config.add_view(CustomerNameAutocomplete, route_name='customers.autocomplete',
                    renderer='json', permission='customers.list')
    config.add_route('customers.autocomplete.phone', '/customers/autocomplete/phone')
    config.add_view(CustomerPhoneAutocomplete, route_name='customers.autocomplete.phone',
                    renderer='json', permission='customers.list')

    # info
    config.add_route('customer.info', '/customers/info')
    config.add_view(customer_info, route_name='customer.info',
                    renderer='json', permission='customers.view')

    CustomersView.defaults(config)
