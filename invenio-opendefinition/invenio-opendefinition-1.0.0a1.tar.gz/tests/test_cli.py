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

"""Test CLI."""

from __future__ import absolute_import, print_function

from click.testing import CliRunner
from invenio_pidstore.models import PersistentIdentifier

from invenio_opendefinition import mappings
from invenio_opendefinition.cli import opendefinition
from invenio_opendefinition.resolvers import license_resolver


def test_loadlicenses(script_info, licenses_example, license_server_mock):
    """Test load licenses."""
    assert PersistentIdentifier.query.count() == 0
    runner = CliRunner()

    # Run twice to test the updating code also
    for x in range(2):
        result = runner.invoke(
            opendefinition,
            ['loadlicenses'],
            obj=script_info
        )
        assert result.exit_code == 0
        for license in licenses_example:
            pid, record = license_resolver.resolve(license)
            del record['$schema']
            assert record == licenses_example[license]

    assert PersistentIdentifier.query.count() == len(licenses_example)
