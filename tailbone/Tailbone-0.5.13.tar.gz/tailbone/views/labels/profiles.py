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
Label Profile Views
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model

import formalchemy
from webhelpers.html import HTML
from pyramid.httpexceptions import HTTPFound

from tailbone.db import Session
from tailbone.views import MasterView
from tailbone.views.continuum import VersionView, version_defaults


class FormatFieldRenderer(formalchemy.TextAreaFieldRenderer):

    def render_readonly(self, **kwargs):
        value = self.raw_value
        if not value:
            return ''
        return HTML.tag('pre', c=value)

    def render(self, **kwargs):
        kwargs.setdefault('size', (80, 8))
        return super(FormatFieldRenderer, self).render(**kwargs)


class ProfilesView(MasterView):
    """
    Master view for the LabelProfile model.
    """
    model_class = model.LabelProfile
    model_title = "Label Profile"
    url_prefix = '/labels/profiles'

    def configure_grid(self, g):
        g.default_sortkey = 'ordinal'
        g.configure(
            include=[
                g.ordinal,
                g.code,
                g.description,
                g.visible,
            ],
            readonly=True)

    def configure_fieldset(self, fs):
        fs.format.set(renderer=FormatFieldRenderer)
        fs.configure(
            include=[
                fs.ordinal,
                fs.code,
                fs.description,
                fs.printer_spec,
                fs.formatter_spec,
                fs.format,
                fs.visible,
            ])

    def after_create(self, profile):
        self.after_edit(profile)

    def after_edit(self, profile):
        if not profile.format:
            formatter = profile.get_formatter(self.rattail_config)
            if formatter:
                try:
                    profile.format = formatter.default_format
                except NotImplementedError:
                    pass


class LabelProfileVersionView(VersionView):
    """
    View which shows version history for a label profile.
    """
    parent_class = model.LabelProfile
    model_title = "Label Profile"
    route_model_list = 'label_profiles'
    route_model_view = 'labelprofiles.view'


def printer_settings(request):
    uuid = request.matchdict['uuid']
    profile = Session.query(model.LabelProfile).get(uuid) if uuid else None
    if not profile:
        return HTTPFound(location=request.route_url('labelprofiles'))

    read_profile = HTTPFound(location=request.route_url(
            'labelprofiles.view', uuid=profile.uuid))

    printer = profile.get_printer(request.rattail_config)
    if not printer:
        request.session.flash("Label profile \"%s\" does not have a functional "
                              "printer spec." % profile)
        return read_profile
    if not printer.required_settings:
        request.session.flash("Printer class for label profile \"%s\" does not "
                              "require any settings." % profile)
        return read_profile

    if request.method == 'POST':
        for setting in printer.required_settings:
            if setting in request.POST:
                profile.save_printer_setting(setting, request.POST[setting])
        return read_profile

    return {'profile': profile, 'printer': printer}


def includeme(config):
    ProfilesView.defaults(config)
    version_defaults(config, LabelProfileVersionView, 'labelprofile', template_prefix='/labels/profiles')

    # edit printer settings
    config.add_route('labelprofiles.printer_settings', '/labels/profiles/{uuid}/printer')
    config.add_view(printer_settings, route_name='labelprofiles.printer_settings',
                    renderer='/labels/profiles/printer.mako',
                    permission='labelprofiles.edit')
