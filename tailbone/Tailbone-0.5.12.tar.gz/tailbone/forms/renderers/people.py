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
People Field Renderers
"""

from __future__ import unicode_literals, absolute_import

from .common import AutocompleteFieldRenderer
from webhelpers.html import tags


__all__ = ['PersonFieldRenderer', 'PersonFieldLinkRenderer',
           'CustomerFieldRenderer', 'CustomerFieldLinkRenderer']


class PersonFieldRenderer(AutocompleteFieldRenderer):
    """
    Renderer for :class:`rattail.db.model.Person` instance fields.
    """

    service_route = 'people.autocomplete'


class PersonFieldLinkRenderer(PersonFieldRenderer):
    """
    Renderer for :class:`rattail.db.model.Person` instance fields (with hyperlink).
    """

    def render_readonly(self, **kwargs):
        person = self.raw_value
        if person:
            return tags.link_to(
                unicode(person),
                self.request.route_url('people.view', uuid=person.uuid))
        return u''


class CustomerFieldRenderer(AutocompleteFieldRenderer):
    """
    Renderer for :class:`rattail.db.model.Customer` instance fields.
    """

    service_route = 'customers.autocomplete'


class CustomerFieldLinkRenderer(CustomerFieldRenderer):
    """
    Renderer for :class:`rattail.db.model.Customer` instance fields (with hyperlink).
    """

    def render_readonly(self, **kwargs):
        customer = self.raw_value
        if customer:
            return tags.link_to(
                unicode(customer),
                self.request.route_url('customers.view', uuid=customer.uuid))
        return u''
