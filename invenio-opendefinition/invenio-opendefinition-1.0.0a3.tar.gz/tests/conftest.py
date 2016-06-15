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

"""Pytest configuration."""

from __future__ import absolute_import, print_function

import json
import os
import shutil
import tempfile
from os.path import dirname, join

import httpretty
import pytest
from elasticsearch.exceptions import RequestError
from flask import Flask
from flask_celeryext import FlaskCeleryExt
from flask_cli import FlaskCLI, ScriptInfo
from invenio_db import InvenioDB, db
from invenio_jsonschemas import InvenioJSONSchemas
from invenio_pidstore import InvenioPIDStore
from invenio_records import InvenioRecords
from invenio_records_rest.utils import PIDConverter
from invenio_search import InvenioSearch, current_search
from sqlalchemy_utils.functions import create_database, database_exists, \
    drop_database

from invenio_opendefinition import InvenioOpenDefinition
from invenio_opendefinition.tasks import create_or_update_license_record


@pytest.yield_fixture
def app(licenses_example):
    """Flask application fixture."""
    instance_path = tempfile.mkdtemp()
    app = Flask('testapp', instance_path=instance_path)
    app.config.update(
        JSONSCHEMAS_HOST='localhost',
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'SQLALCHEMY_DATABASE_URI', 'sqlite://'),
        TESTING=True,
        RECORDS_REST_DEFAULT_READ_PERMISSION_FACTORY=None,
        CELERY_ALWAYS_EAGER=True,
        CELERY_RESULT_BACKEND="cache",
        CELERY_CACHE_BACKEND="memory",
        CELERY_EAGER_PROPAGATES_EXCEPTIONS=True,
    )

    app.url_map.converters['pid'] = PIDConverter

    FlaskCeleryExt(app)
    FlaskCLI(app)
    InvenioDB(app)
    InvenioJSONSchemas(app)
    InvenioRecords(app)
    InvenioPIDStore(app)
    InvenioOpenDefinition(app)

    with app.app_context():
        if str(db.engine.url) != "sqlite://" and \
           not database_exists(str(db.engine.url)):
            create_database(str(db.engine.url))
        db.drop_all()
        db.create_all()

    def teardown():
        drop_database(str(db.engine.url))

    yield app

    shutil.rmtree(instance_path)


@pytest.yield_fixture
def script_info(app):
    """CLI object."""
    with app.app_context():
        yield ScriptInfo(create_app=lambda info: app)


@pytest.fixture
def loaded_example_licenses(app, licenses_example):
    with app.app_context():
        for key in licenses_example:
            create_or_update_license_record(licenses_example[key])
    for key in licenses_example:
        licenses_example[key]['$schema'] = 'http://{0}{1}/{2}'.format(
            app.config['JSONSCHEMAS_HOST'],
            app.config['JSONSCHEMAS_ENDPOINT'],
            app.config['OPENDEFINITION_SCHEMAS_DEFAULT_LICENSE']
        )
    return licenses_example


@pytest.yield_fixture
def license_server_mock(app, licenses_example):
    httpretty.register_uri(
        httpretty.GET,
        app.config['OPENDEFINITION_LICENSES_URL'],
        body=json.dumps(licenses_example),
        content_type='application/json'
    )
    httpretty.enable()
    yield
    httpretty.disable()


@pytest.fixture(scope="session")
def licenses_example():
    path = dirname(__file__)
    with open(join(
            path,
            'data',
            'all-licenses.json')) as file:
        return json.load(file)


@pytest.yield_fixture
def es(app):
    """Provide elasticsearch access."""
    app.config.update(dict(
        SEARCH_AUTOINDEX=[],
    ))
    InvenioSearch(app)
    with app.app_context():
        try:
            list(current_search.create())
        except RequestError:
            list(current_search.delete(ignore=[404]))
            list(current_search.create())
        yield current_search
        list(current_search.delete(ignore=[404]))
