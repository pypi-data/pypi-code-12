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
Brand Views
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model

from tailbone.views import MasterView, AutocompleteView
from tailbone.views.continuum import VersionView, version_defaults


class BrandsView(MasterView):
    """
    Master view for the Brand class.
    """
    model_class = model.Brand

    def configure_grid(self, g):
        g.filters['name'].default_active = True
        g.filters['name'].default_verb = 'contains'
        g.default_sortkey = 'name'
        g.configure(
            include=[
                g.name,
            ],
            readonly=True)

    def configure_fieldset(self, fs):
        fs.configure(
            include=[
                fs.name,
            ])
        return fs


class BrandVersionView(VersionView):
    """
    View which shows version history for a brand.
    """
    parent_class = model.Brand
    route_model_view = 'brands.view'


class BrandsAutocomplete(AutocompleteView):

    mapped_class = model.Brand
    fieldname = 'name'


def includeme(config):

    # autocomplete
    config.add_route('brands.autocomplete', '/brands/autocomplete')
    config.add_view(BrandsAutocomplete, route_name='brands.autocomplete',
                    renderer='json', permission='brands.list')

    BrandsView.defaults(config)
    version_defaults(config, BrandVersionView, 'brand')
