# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
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

"""Invenio-Accounts utility functions for tests and testing purposes.

.. warning:: DO NOT USE IN A PRODUCTION ENVIRONMENT.

Functions within accessing the datastore will throw an error if called outside
of an application context. If pytest-flask is installed you don't have to worry
about this.
"""

from __future__ import absolute_import, print_function

import datetime

import flask
import flask_login
from flask import current_app
from flask_kvsession import SessionID
from flask_security import url_for_security
from flask_security.utils import encrypt_password
from werkzeug.local import LocalProxy

# "Convenient references" (lifted from flask_security source)
_datastore = LocalProxy(lambda: current_app.extensions['security'].datastore)


def create_test_user(email='test@test.org',
                     password='123456', **kwargs):
    """Create a user in the datastore, bypassing the registration process.

    Accesses the application's datastore. An error is thrown if called from
    outside of an application context.

    Returns the created user model object instance, with the plaintext password
    as `user.password_plaintext`.
    """
    assert flask.current_app.testing
    encrypted_password = encrypt_password(password)
    user = _datastore.create_user(email=email, password=encrypted_password,
                                  **kwargs)
    _datastore.commit()
    user.password_plaintext = password
    return user


def login_user_via_view(client, email=None, password=None, user=None,
                        login_url=None):
    r"""Attempt to log the given user in via the 'login' view on the client.

    :param client: client to send the request from.
    :param email: email of user account to log in with.
    :param password: password of user account to log in with.
    :param user: If present, ``user.email`` and ``user.password_plaintext`` \
        take precedence over the `email` and `password` parameters.
    :type user: :class:`invenio_accounts.models.User` (with the addition of \
        a ``password_plaintext`` field)
    :param login_url: URL to post login details to. Defaults to the current \
        application's login URL.

    :returns: The response object from the POST to the login form.
    """
    if user is not None:
        email = user.email
        password = user.password_plaintext
    return client.post(login_url or url_for_security('login'),
                       data={'email': email, 'password': password},
                       environ_base={'REMOTE_ADDR': '127.0.0.1'})
    # If the REMOTE_ADDR isn't set it'll throw out a ValueError as it attempts
    # to update the User model in the database with 'untrackable' as the new
    # `last_login_ip`.


def client_authenticated(client, test_url=None):
    r"""Attempt to access the change password page with the given client.

    :param test_url: URL to attempt to get. Defaults to the current \
            application's "change password" page.
    :returns: True if the client can get the test_url without getting \
        redirected and ``flask_login.current_user`` is not anonymous \
        after requesting the page.
    """
    response = client.get(test_url or url_for_security('change_password'))

    return (response.status_code == 200 and
            not flask_login.current_user.is_anonymous)


def webdriver_authenticated(webdriver, test_url=None):
    """Attempt to get the change password page through the given webdriver.

    Similar to `client_authenticated`, but for selenium webdriver objects.
    """
    save_url = webdriver.current_url

    webdriver.get(test_url or flask.url_for('security.change_password',
                                            _external=True))
    result_url = webdriver.current_url
    webdriver.get(save_url)
    return (flask.url_for('security.login', _external=True) not in result_url)


def unserialize_session(sid_s):
    """Return the unserialized session."""
    return SessionID.unserialize(sid_s)
