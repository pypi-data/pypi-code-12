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
Database Utilities
"""

from __future__ import unicode_literals, absolute_import

import re
import pprint
import logging

from sqlalchemy import orm

# TODO: Deprecate/remove these imports.
from rattail.db.config import engine_from_config, get_engines, get_default_engine, configure_session


log = logging.getLogger(__name__)


class QuerySequence(object):
    """
    Simple wrapper for a SQLAlchemy (or Django, or other?) query, to make it
    sort of behave like a normal sequence, as much as needed to e.g. make an
    importer happy.
    """

    def __init__(self, query):
        self.query = query

    def __len__(self):
        return self.query.count()

    def __iter__(self):
        return iter(self.query)


def maxlen(attr):
    """
    Return the maximum length for the given attribute.
    """
    if len(attr.property.columns) == 1:
        type_ = attr.property.columns[0].type
        return getattr(type_, 'length', None)


def make_topo_sortkey(model, metadata=None):
    """
    Returns a function suitable for use as a ``key`` kwarg to a standard Python
    sorting call.  This key function will expect a single class mapper and
    return a sequence number associated with that model.  The sequence is
    determined by SQLAlchemy's topological table sorting.
    """
    if metadata is None:
        metadata = model.Base.metadata

    tables = {}
    for i, table in enumerate(metadata.sorted_tables, 1):
        tables[table.name] = i

    log.debug("topo sortkeys for '{}' will be:\n{}".format(model.__name__, pprint.pformat(
        [(i, name) for name, i in sorted(tables.iteritems(), key=lambda t: t[1])])))

    def sortkey(name):
        mapper = orm.class_mapper(getattr(model, name))
        return tuple(tables[t.name] for t in mapper.tables)

    return sortkey


def normalize_full_name(first_name, last_name):
    """
    Normalize the given first and last name to a "full" name value.  The
    fallback return value is an empty string.
    """
    first_name = (first_name or '').strip()
    last_name = (last_name or '').strip()
    if first_name and last_name:
        return "{} {}".format(first_name, last_name)
    if first_name:
        return first_name
    if last_name:
        return last_name
    return ''


def normalize_phone_number(number):
    """
    Normalize a phone number to digits only.
    """
    if number is not None:
        return re.sub(r'\D', '', number)


def format_phone_number(number):
    """
    Returns a phone number in ``(XXX) XXX-XXXX`` format if possible; otherwise
    returns the argument unaltered.
    """
    original, number = number, normalize_phone_number(number)
    if number and len(number) == 10:
        return '({}) {}-{}'.format(number[:3], number[3:6], number[6:])
    return original
