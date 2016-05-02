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
FormAlchemy Grid Classes
"""

from __future__ import unicode_literals, absolute_import

import logging

import sqlalchemy as sa
from sqlalchemy import orm

from edbob.util import prettify

from rattail.db.types import GPCType

import formalchemy
from webhelpers import paginate

from tailbone.db import Session
from tailbone.newgrids import Grid, GridColumn, filters


log = logging.getLogger(__name__)


class AlchemyGrid(Grid):
    """
    Grid class for use with SQLAlchemy data models.

    Note that this is partially just a wrapper around the FormAlchemy grid, and
    that you may use this in much the same way, e.g.::

       grid = AlchemyGrid(...)
       grid.configure(
           include=[
               field1,
               field2,
           ])
       grid.append(field3)
       del grid.field1
       grid.field2.set(renderer=SomeFieldRenderer)
    """

    def __init__(self, *args, **kwargs):
        super(AlchemyGrid, self).__init__(*args, **kwargs)
        fa_grid = formalchemy.Grid(self.model_class, instances=self.data,
                                   session=kwargs.get('session', Session()),
                                   request=self.request)
        fa_grid.prettify = prettify
        self._fa_grid = fa_grid

    def __delattr__(self, attr):
        delattr(self._fa_grid, attr)

    def __getattr__(self, attr):
        return getattr(self._fa_grid, attr)

    def default_filters(self):
        """
        SQLAlchemy grids are able to provide a default set of filters based on
        the column properties mapped to the model class.
        """
        filtrs = filters.GridFilterSet()
        mapper = orm.class_mapper(self.model_class)
        for prop in mapper.iterate_properties:
            if isinstance(prop, orm.ColumnProperty) and not prop.key.endswith('uuid'):
                filtrs[prop.key] = self.make_filter(prop.key, prop.columns[0])
        return filtrs

    def make_filter(self, key, column, **kwargs):
        """
        Make a filter suitable for use with the given column.
        """
        factory = filters.AlchemyGridFilter
        if isinstance(column.type, sa.String):
            factory = filters.AlchemyStringFilter
        elif isinstance(column.type, sa.Numeric):
            factory = filters.AlchemyNumericFilter
        elif isinstance(column.type, sa.Integer):
            factory = filters.AlchemyNumericFilter
        elif isinstance(column.type, sa.Boolean):
            factory = filters.AlchemyBooleanFilter
        elif isinstance(column.type, sa.Date):
            factory = filters.AlchemyDateFilter
        elif isinstance(column.type, sa.DateTime):
            factory = filters.AlchemyDateTimeFilter
        elif isinstance(column.type, GPCType):
            factory = filters.AlchemyGPCFilter
        factory = kwargs.pop('factory', factory)
        return factory(key, column=column, config=self.request.rattail_config, **kwargs)

    def iter_filters(self):
        """
        Iterate over the grid's complete set of filters.
        """
        return self.filters.itervalues()

    def filter_data(self, query):
        """
        Filter and return the given data set, according to current settings.
        """
        # This overrides the core version only slightly, in that it will only
        # invoke a join if any particular filter(s) actually modifies the
        # query.  The main motivation for this is on the products page, where
        # the tricky "vendor (any)" filter has a weird join and causes
        # unpredictable results.  Now we can skip the join for that unless the
        # user actually enters some criteria for it.
        for filtr in self.iter_active_filters():
            original = query
            query = filtr.filter(query)
            if query is not original and filtr.key in self.joiners and filtr.key not in self.joined:
                query = self.joiners[filtr.key](query)
                self.joined.add(filtr.key)
        return query

    def make_sorters(self, sorters):
        """
        Returns a mapping of sort options for the grid.  Keyword args override
        the defaults, which are obtained via the SQLAlchemy ORM.
        """
        sorters, updates = {}, sorters
        mapper = orm.class_mapper(self.model_class)
        for prop in mapper.iterate_properties:
            if isinstance(prop, orm.ColumnProperty) and not prop.key.endswith('uuid'):
                sorters[prop.key] = self.make_sorter(prop)
        if updates:
            sorters.update(updates)
        return sorters

    def make_sorter(self, model_property):
        """
        Returns a function suitable for a sort map callable, with typical logic
        built in for sorting applied to ``field``.
        """
        class_ = getattr(model_property, 'class_', self.model_class)
        column = getattr(class_, model_property.key)
        return lambda q, d: q.order_by(getattr(column, d)())

    def load_settings(self):
        """
        When a SQLAlchemy grid loads its settings, it must update the
        underlying FormAlchemy grid instance with the final (filtered/etc.)
        data set.
        """
        super(AlchemyGrid, self).load_settings()
        self._fa_grid.rebind(self.make_visible_data(), session=Session(),
                             request=self.request)

    def paginate_data(self, query):
        """
        Paginate the given data set according to current settings, and return
        the result.
        """
        return paginate.Page(
            query, item_count=query.count(),
            items_per_page=self.pagesize, page=self.page,
            url=paginate.PageURL_WebOb(self.request))

    def iter_visible_columns(self):
        """
        Returns an iterator for all currently-visible columns.
        """
        for field in self._fa_grid.render_fields.itervalues():
            column = GridColumn(field.key, label=field.label(),
                                title=getattr(field, '_column_header_title', None))
            column.field = field
            yield column

    def iter_rows(self):
        for row in self._fa_grid.rows:
            self._fa_grid._set_active(row, orm.object_session(row))
            yield row

    def get_row_key(self, row):
        mapper = orm.object_mapper(row)
        assert len(mapper.primary_key) == 1
        return getattr(row, mapper.primary_key[0].key)

    def render_cell(self, row, column):
        return column.field.render_readonly()
