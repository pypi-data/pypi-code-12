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

"""Invenio mail module."""

from __future__ import absolute_import, print_function

import sys
import threading

from flask_mail import Mail, email_dispatched


def print_email(message, app):
    """Print mail to stream.

    Signal handler for email_dispatched signal. Prints by default the output
    to the stream specified in the constructor of InvenioMail.

    :param message: Message object.
    :param app: Flask application object.
    """
    invenio_mail = app.extensions['invenio-mail']
    with invenio_mail._lock:
        invenio_mail.stream.write(
            "{0}\n{1}\n".format(message.as_string(), '-' * 79))
        invenio_mail.stream.flush()


class InvenioMail(object):
    """Invenio-Mail extension.

    Mails are only printed to the stream if ``MAIL_SUPPRESS_SEND`` is ``True``.

    :param app: Flask application object.
    :param stream: Stream to print emails to. Defaults to ``sys.stdout``.
    """

    def __init__(self, app=None, stream=None):
        """Extension initialization."""
        self.stream = stream or sys.stdout
        self._lock = threading.RLock()
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        if 'mail' not in app.extensions:
            Mail(app)
        if app.config.get('MAIL_SUPPRESS_SEND', False) or app.debug:
            email_dispatched.connect(print_email)
        app.extensions['invenio-mail'] = self

    def init_config(self, app):
        """Initialize configuration."""
        app.config.setdefault('MAIL_DEBUG', app.debug)
        app.config.setdefault('MAIL_SUPPRESS_SEND', app.debug or app.testing)
