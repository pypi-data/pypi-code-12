# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
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


"""Module tests."""

from __future__ import absolute_import, print_function

import sys

from flask import Flask
from flask_mail import Message

from invenio_mail import InvenioMail

PY3 = sys.version_info[0] == 3

if PY3:
    from io import StringIO
else:
    from StringIO import StringIO


def test_version():
    """Test version import."""
    from invenio_mail import __version__
    assert __version__


def test_init():
    """Test extension initialization."""
    app = Flask('testapp')
    ext = InvenioMail(app)
    assert 'invenio-mail' in app.extensions

    app = Flask('testapp')
    ext = InvenioMail()
    assert 'invenio-mail' not in app.extensions
    ext.init_app(app)
    assert 'invenio-mail' in app.extensions


def test_print_email():
    """Test printing of email."""
    app = Flask('testapp')
    app.config.update(MAIL_SUPPRESS_SEND=True)

    output = StringIO()
    InvenioMail(app, stream=output)

    with app.app_context():
        msg = Message(
            "Test subject", sender="from@example.com",
            recipients=["to@example.com"], body="Test Body")
        app.extensions['mail'].send(msg)

    email = output.getvalue()
    output.close()

    sep = '\r\n' if PY3 else '\n'

    assert "Subject: Test subject%s" % sep in email
    assert "From: from@example.com%s" % sep in email
    assert "To: to@example.com%s" % sep in email
    assert "{0}{0}Test Body".format(sep) in email
