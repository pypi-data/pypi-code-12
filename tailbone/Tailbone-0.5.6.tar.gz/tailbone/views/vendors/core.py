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
Vendor Views
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model

from tailbone import forms
from tailbone.db import Session
from tailbone.views import MasterView, AutocompleteView
from tailbone.views.continuum import VersionView, version_defaults


class VendorsView(MasterView):
    """
    Master view for the Vendor class.
    """
    model_class = model.Vendor

    def configure_grid(self, g):
        g.filters['name'].default_active = True
        g.filters['name'].default_verb = 'contains'
        g.filters['id'].label = "ID"
        g.default_sortkey = 'name'

        g.append(forms.AssociationProxyField('contact'))
        g.configure(
            include=[
                g.id.label("ID"),
                g.name,
                g.phone.label("Phone Number"),
                g.email.label("Email Address"),
                g.contact,
            ],
            readonly=True)

    def configure_fieldset(self, fs):
        fs.append(forms.AssociationProxyField('contact'))
        fs.configure(
            include=[
                fs.id.label("ID"),
                fs.name,
                fs.special_discount,
                fs.lead_time_days.label("Lead Time in Days"),
                fs.order_interval_days.label("Order Interval in Days"),
                fs.phone.label("Phone Number").readonly(),
                fs.email.label("Email Address").readonly(),
                fs.contact.with_renderer(forms.PersonFieldRenderer).readonly(),
            ])

    def before_delete(self, vendor):
        # Remove all product costs.
        q = Session.query(model.ProductCost).filter(
            model.ProductCost.vendor == vendor)
        for cost in q:
            Session.delete(cost)


class VendorVersionView(VersionView):
    """
    View which shows version history for a vendor.
    """
    parent_class = model.Vendor
    route_model_view = 'vendors.view'


class VendorsAutocomplete(AutocompleteView):

    mapped_class = model.Vendor
    fieldname = 'name'


def includeme(config):

    # autocomplete
    config.add_route('vendors.autocomplete', '/vendors/autocomplete')
    config.add_view(VendorsAutocomplete, route_name='vendors.autocomplete',
                    renderer='json', permission='vendors.list')

    VendorsView.defaults(config)
    version_defaults(config, VendorVersionView, 'vendor')
