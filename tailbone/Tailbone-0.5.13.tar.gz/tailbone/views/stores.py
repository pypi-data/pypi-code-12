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
Store Views
"""

from __future__ import unicode_literals, absolute_import

import sqlalchemy as sa

from rattail.db import model

from tailbone.views import MasterView


class StoresView(MasterView):
    """
    Master view for the Store class.
    """
    model_class = model.Store

    def configure_grid(self, g):

        g.joiners['email'] = lambda q: q.outerjoin(model.StoreEmailAddress, sa.and_(
            model.StoreEmailAddress.parent_uuid == model.Store.uuid,
            model.StoreEmailAddress.preference == 1))
        g.joiners['phone'] = lambda q: q.outerjoin(model.StorePhoneNumber, sa.and_(
            model.StorePhoneNumber.parent_uuid == model.Store.uuid,
            model.StorePhoneNumber.preference == 1))

        g.filters['email'] = g.make_filter('email', model.StoreEmailAddress.address,
                                           label="Email Address")
        g.filters['phone'] = g.make_filter('phone', model.StorePhoneNumber.number,
                                           label="Phone Number")

        g.filters['name'].default_active = True
        g.filters['name'].default_verb = 'contains'
        g.filters['id'].label = "ID"

        g.sorters['email'] = lambda q, d: q.order_by(getattr(model.StoreEmailAddress.address, d)())
        g.sorters['phone'] = lambda q, d: q.order_by(getattr(model.StorePhoneNumber.number, d)())

        g.default_sortkey = 'id'

        g.configure(
            include=[
                g.id.label("ID"),
                g.name,
                g.phone.label("Phone Number"),
                g.email.label("Email Address"),
            ],
            readonly=True)

    def configure_fieldset(self, fs):
        fs.configure(
            include=[
                fs.id.label("ID"),
                fs.name,
                fs.database_key,
                fs.phone.label("Phone Number").readonly(),
                fs.email.label("Email Address").readonly(),
            ])


def includeme(config):
    StoresView.defaults(config)
