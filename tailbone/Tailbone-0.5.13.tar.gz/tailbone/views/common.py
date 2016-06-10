# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2016 Lance Edgar
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
Various common views
"""

from __future__ import unicode_literals, absolute_import

from rattail.mail import send_email

import formencode
from pyramid import httpexceptions
from formencode import validators
from pyramid_simpleform import Form

from tailbone import forms


class Feedback(formencode.Schema):
    """
    Form schema for user feedback.
    """
    allow_extra_fields = True
    user = forms.validators.ValidUser()
    user_name = validators.NotEmpty()
    message = validators.NotEmpty()


def feedback(request):
    """
    Generic view to present/handle the user feedback form.
    """
    form = Form(request, schema=Feedback)
    if form.validate():
        data = dict(form.data)
        if data['user']:
            data['user_url'] = request.route_url('users.view', uuid=data['user'].uuid)
        send_email(request.rattail_config, 'user_feedback', data=data)
        request.session.flash("Thank you for your feedback.")
        return httpexceptions.HTTPFound(location=form.data['referrer'])
    return {'form': forms.FormRenderer(form)}


def includeme(config):
    config.add_route('feedback', '/feedback')
    config.add_view(feedback, route_name='feedback', renderer='/feedback.mako')
