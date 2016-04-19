# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Implementention of various utility functions."""

import six

from flask import current_app, request
from werkzeug.utils import import_string


def obj_or_import_string(value, default=None):
    """Import string or return object."""
    if isinstance(value, six.string_types):
        return import_string(value)
    elif value:
        return value
    return default


def load_or_import_from_config(key, app=None, default=None):
    """Load or import value from config."""
    app = app or current_app
    imp = app.config.get(key)
    return obj_or_import_string(imp, default=default)


def allow_all(*args, **kwargs):
    """Return permission that always allow an access."""
    return type('Allow', (), {'can': lambda self: True})()


def deny_all(*args, **kwargs):
    """Return permission that always deny an access."""
    return type('Deny', (), {'can': lambda self: False})()


def check_elasticsearch(record, *args, **kwargs):
    """Return permission that check if the record exists in ES index."""
    def can(self):
        """Try to search for given record."""
        search = request._methodview.search_class()
        search = search.get_record(str(record.id))
        return search.count() == 1

    return type('CheckES', (), {'can': can})()
