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

"""Invenio module integrating Invenio repositories and OpenDefinition."""

from __future__ import absolute_import, print_function

OPENDEFINITION_LICENSES_URL = \
    'http://licenses.opendefinition.org/licenses/groups/all.json'

OPENDEFINITION_SCHEMAS_DEFAULT_LICENSE = 'licenses/license-v1.0.0.json'

OPENDEFINITION_JSONRESOLVER_HOST = 'inveniosoftware.org'

OPENDEFINITION_REST_ENDPOINTS = dict(
    od_lic=dict(
        pid_type='od_lic',
        pid_minter='opendefinition_license_minter',
        pid_fetcher='opendefinition_license_fetcher',
        list_route='/licenses/',
        item_route='/licenses/<pid(od_lic):pid_value>',
        search_index='licenses',
        search_type=None,
        record_serializers={
            'application/json': (
                'invenio_records_rest.serializers:json_v1_response'),
        },
        search_serializers={
            'application/json': (
                'invenio_records_rest.serializers:json_v1_search'),
        },
        default_media_type='application/json',
        suggesters={
            'text': {
                'completion': {
                    'field': 'suggest',
                }
            }
        },
    ),
)
