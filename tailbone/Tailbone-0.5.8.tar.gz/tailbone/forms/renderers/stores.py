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
Store Field Renderers
"""

from __future__ import unicode_literals

from formalchemy.fields import SelectFieldRenderer


class StoreFieldRenderer(SelectFieldRenderer):
    """
    Renderer for :class:`rattail.db.model.Store` instance fields.
    """

    def render_readonly(self, **kwargs):
        store = self.raw_value
        if not store:
            return ''
        return '{0} - {1}'.format(store.id, store.name)
