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

from __future__ import absolute_import, print_function

import json

from invenio_pidstore.models import PersistentIdentifier
from invenio_records_rest import InvenioRecordsREST

from invenio_opendefinition.config import OPENDEFINITION_REST_ENDPOINTS
from invenio_opendefinition.tasks import harvest_licenses


def test_records_rest(app, es, loaded_example_licenses):
    """Test Records REST."""
    app.config['RECORDS_REST_ENDPOINTS'] = OPENDEFINITION_REST_ENDPOINTS
    InvenioRecordsREST(app)
    assert PersistentIdentifier.query.count() == 109

    with app.test_client() as client:
        resp = client.get('/licenses/MIT')
        assert resp.status_code == 200
        resp_json = json.loads(resp.get_data(as_text=True))
        assert resp_json['metadata'] == loaded_example_licenses['MIT']

        resp = client.get('/licenses/')
        assert resp.status_code == 200
