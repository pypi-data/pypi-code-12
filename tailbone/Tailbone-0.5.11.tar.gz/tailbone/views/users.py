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
User Views
"""

from __future__ import unicode_literals, absolute_import

from sqlalchemy import orm

from rattail.db import model
from rattail.db.auth import guest_role, set_user_password

import formalchemy
from formalchemy.fields import SelectFieldRenderer
from webhelpers.html import HTML, tags

from tailbone.db import Session
from tailbone.views import MasterView
from tailbone.views.continuum import VersionView, version_defaults
from tailbone.forms import renderers


def unique_username(value, field):
    user = field.parent.model
    query = Session.query(model.User).filter(model.User.username == value)
    if user.uuid:
        query = query.filter(model.User.uuid != user.uuid)
    if query.count():
        raise formalchemy.ValidationError("Username must be unique.")


def passwords_match(value, field):
    if field.parent.confirm_password.value != value:
        raise formalchemy.ValidationError("Passwords do not match")
    return value


class PasswordFieldRenderer(formalchemy.PasswordFieldRenderer):

    def render(self, **kwargs):
        return tags.password(self.name, value='', maxlength=self.length, **kwargs)


class PasswordField(formalchemy.Field):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('value', lambda x: x.password)
        kwargs.setdefault('renderer', PasswordFieldRenderer)
        kwargs.setdefault('validate', passwords_match)
        super(PasswordField, self).__init__(*args, **kwargs)

    def sync(self):
        if not self.is_readonly():
            password = self.renderer.deserialize()
            if password:
                set_user_password(self.model, password)


def RolesFieldRenderer(request):

    class RolesFieldRenderer(SelectFieldRenderer):

        def render_readonly(self, **kwargs):
            roles = Session.query(model.Role)
            html = ''
            for uuid in self.value:
                role = roles.get(uuid)
                link = tags.link_to(
                    role.name, request.route_url('roles.view', uuid=role.uuid))
                html += HTML.tag('li', c=link)
            html = HTML.tag('ul', c=html)
            return html

    return RolesFieldRenderer


class RolesField(formalchemy.Field):

    def __init__(self, name, **kwargs):
        kwargs.setdefault('value', self.get_value)
        kwargs.setdefault('options', self.get_options())
        kwargs.setdefault('multiple', True)
        super(RolesField, self).__init__(name, **kwargs)

    def get_value(self, user):
        return [x.uuid for x in user.roles]

    def get_options(self):
        return Session.query(model.Role.name, model.Role.uuid)\
            .filter(model.Role.uuid != guest_role(Session()).uuid)\
            .order_by(model.Role.name)\
            .all()

    def sync(self):
        if not self.is_readonly():
            user = self.model
            roles = Session.query(model.Role)
            data = self.renderer.deserialize()
            user.roles = [roles.get(x) for x in data]
                

class UsersView(MasterView):
    """
    Master view for the User model.
    """
    model_class = model.User

    def query(self, session):
        return session.query(model.User)\
                      .options(orm.joinedload(model.User.person))

    def configure_grid(self, g):
        g.joiners['person'] = lambda q: q.outerjoin(model.Person)

        del g.filters['password']
        del g.filters['salt']
        g.filters['username'].default_active = True
        g.filters['username'].default_verb = 'contains'
        g.filters['active'].default_active = True
        g.filters['active'].default_verb = 'is_true'
        g.filters['person'] = g.make_filter('person', model.Person.display_name, label="Person's Name",
                                            default_active=True, default_verb='contains')
        g.filters['password'] = g.make_filter('password', model.User.password,
                                              verbs=['is_null', 'is_not_null'])

        g.sorters['person'] = lambda q, d: q.order_by(getattr(model.Person.display_name, d)())
        g.default_sortkey = 'username'

        g.person.set(label="Person's Name")
        g.configure(
            include=[
                g.username,
                g.person,
            ],
            readonly=True)

    def configure_fieldset(self, fs):
        fs.username.set(validate=unique_username)
        fs.person.set(options=[])
        fs.person.set(renderer=renderers.PersonFieldLinkRenderer)
        fs.append(PasswordField('password', label="Set Password"))
        fs.password.attrs(autocomplete='off')
        fs.append(formalchemy.Field('confirm_password', renderer=PasswordFieldRenderer))
        fs.confirm_password.attrs(autocomplete='off')
        fs.append(RolesField('roles', renderer=RolesFieldRenderer(self.request)))
        fs.configure(
            include=[
                fs.username,
                fs.person,
                fs.active,
                fs.password,
                fs.confirm_password,
                fs.roles,
            ])
        if self.viewing:
            del fs.password
            del fs.confirm_password


class UserVersionView(VersionView):
    """
    View which shows version history for a user.
    """
    parent_class = model.User
    route_model_view = 'users.view'


def includeme(config):
    UsersView.defaults(config)
    version_defaults(config, UserVersionView, 'user')
