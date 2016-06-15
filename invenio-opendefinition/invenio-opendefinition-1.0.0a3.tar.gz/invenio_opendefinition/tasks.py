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

"""Celery tasks."""

from __future__ import absolute_import, print_function

import requests
from celery import shared_task
from flask import current_app
from invenio_db import db
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_records.api import Record

from .minters import license_minter
from .resolvers import license_resolver
from .validators import license_validator


@shared_task(ignore_result=True)
def harvest_licenses():
    """Harvest OpenDefinition licenses."""
    response = requests.get(current_app.config['OPENDEFINITION_LICENSES_URL'])
    licenses = response.json()
    for license in licenses:
        license_validator.validate(license)
        create_or_update_license_record.delay(licenses[license])


@shared_task(ignore_result=True)
def create_or_update_license_record(license):
    """Register a license."""
    license['$schema'] = 'http://{0}{1}/{2}'.format(
        current_app.config['JSONSCHEMAS_HOST'],
        current_app.config['JSONSCHEMAS_ENDPOINT'],
        current_app.config['OPENDEFINITION_SCHEMAS_DEFAULT_LICENSE']
    )

    try:
        pid, record = license_resolver.resolve(license['id'])
        record.update(license)
        record.commit()
        db.session.commit()
    except PIDDoesNotExistError:
        record = Record.create(license)
        license_minter(record.id, license)
        db.session.commit()
