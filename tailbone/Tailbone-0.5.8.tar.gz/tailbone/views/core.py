# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2015 Lance Edgar
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
Base View Class
"""

from __future__ import unicode_literals

from rattail.db import model

from tailbone.db import Session


class View(object):
    """
    Base class for all class-based views.
    """

    def __init__(self, request):
        self.request = request

    @property
    def rattail_config(self):
        """
        Reference to the effective Rattail config object.
        """
        return self.request.rattail_config

    def late_login_user(self):
        """
        Returns the :class:`rattail:rattail.db.model.User` instance
        corresponding to the "late login" form data (if any), or ``None``.
        """
        if self.request.method == 'POST':
            uuid = self.request.POST.get('late-login-user')
            if uuid:
                return Session.query(model.User).get(uuid)


def fake_error(request):
    """
    View which raises a fake error, to test exception handling.
    """
    raise Exception("Fake error, to test exception handling.")


def includeme(config):
    config.add_route('fake_error', '/fake-error')
    config.add_view(fake_error, route_name='fake_error',
                    permission='admin')
