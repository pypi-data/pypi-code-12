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
Views for Email Bounces
"""

from __future__ import unicode_literals, absolute_import

import os
import datetime

from rattail.db import model
from rattail.bouncer import get_handler
from rattail.bouncer.config import get_profile_keys

import formalchemy
from pyramid.response import FileResponse
from webhelpers.html import literal

from tailbone import newgrids as grids
from tailbone.db import Session
from tailbone.views import MasterView
from tailbone.forms.renderers.bouncer import BounceMessageFieldRenderer


class EmailBouncesView(MasterView):
    """
    Master view for email bounces.
    """
    model_class = model.EmailBounce
    model_title_plural = "Email Bounces"
    url_prefix = '/email-bounces'
    creatable = False
    editable = False

    def __init__(self, request):
        super(EmailBouncesView, self).__init__(request)
        self.handler_options = [('', '(any)')] + sorted(get_profile_keys(self.rattail_config))

    def get_handler(self, bounce):
        return get_handler(self.rattail_config, bounce.config_key)

    def configure_grid(self, g):
        g.joiners['processed_by'] = lambda q: q.outerjoin(model.User)
        g.filters['config_key'].default_active = True
        g.filters['config_key'].default_verb = 'equal'
        g.filters['config_key'].label = "Source"
        g.filters['config_key'].set_value_renderer(grids.filters.ChoiceValueRenderer(self.handler_options))
        g.filters['bounce_recipient_address'].label = "Bounced To"
        g.filters['intended_recipient_address'].label = "Intended For"
        g.filters['processed'].default_active = True
        g.filters['processed'].default_verb = 'is_null'
        g.filters['processed_by'] = g.make_filter('processed_by', model.User.username)
        g.sorters['processed_by'] = g.make_sorter(model.User.username)
        g.default_sortkey = 'bounced'
        g.default_sortdir = 'desc'
        g.configure(
            include=[
                g.config_key.label("Source"),
                g.bounced,
                g.bounce_recipient_address.label("Bounced To"),
                g.intended_recipient_address.label("Intended For"),
                g.processed_by,
            ],
            readonly=True)

    def configure_fieldset(self, fs):
        bounce = fs.model
        handler = self.get_handler(bounce)
        fs.append(formalchemy.Field('message',
                                    value=handler.msgpath(bounce),
                                    renderer=BounceMessageFieldRenderer.new(self.request, handler)))
        fs.append(formalchemy.Field('links',
                                    value=list(handler.make_links(Session(), bounce.intended_recipient_address)),
                                    renderer=LinksFieldRenderer))
        fs.configure(
            include=[
                fs.config_key.label("Source"),
                fs.message,
                fs.bounced,
                fs.bounce_recipient_address.label("Bounced To"),
                fs.intended_recipient_address.label("Intended For"),
                fs.links,
                fs.processed,
                fs.processed_by,
            ],
            readonly=True)
        if not bounce.processed:
            del fs.processed
            del fs.processed_by

    def template_kwargs_view(self, **kwargs):
        bounce = kwargs['instance']
        kwargs['bounce'] = bounce
        handler = self.get_handler(bounce)
        kwargs['handler'] = handler
        with open(handler.msgpath(bounce), 'rb') as f:
            kwargs['message'] = f.read()
        return kwargs

    def process(self):
        """
        View for marking a bounce as processed.
        """
        bounce = self.get_instance()
        bounce.processed = datetime.datetime.utcnow()
        bounce.processed_by = self.request.user
        self.request.session.flash("Email bounce has been marked processed.")
        return self.redirect(self.request.route_url('emailbounces'))

    def unprocess(self):
        """
        View for marking a bounce as *unprocessed*.
        """
        bounce = self.get_instance()
        bounce.processed = None
        bounce.processed_by = None
        self.request.session.flash("Email bounce has been marked UN-processed.")
        return self.redirect(self.request.route_url('emailbounces'))

    def download(self):
        """
        View for downloading the message file associated with a bounce.
        """
        bounce = self.get_instance()
        handler = self.get_handler(bounce)
        path = handler.msgpath(bounce)
        response = FileResponse(path, request=self.request)
        response.headers[b'Content-Length'] = str(os.path.getsize(path))
        response.headers[b'Content-Disposition'] = b'attachment; filename="bounce.eml"'
        return response

    @classmethod
    def defaults(cls, config):

        # mark bounce as processed
        config.add_route('emailbounces.process', '/email-bounces/{uuid}/process')
        config.add_view(cls, attr='process', route_name='emailbounces.process',
                        permission='emailbounces.process')
        config.add_tailbone_permission('emailbounces', 'emailbounces.process',
                                       "Mark Email Bounce as processed")

        # mark bounce as *not* processed
        config.add_route('emailbounces.unprocess', '/email-bounces/{uuid}/unprocess')
        config.add_view(cls, attr='unprocess', route_name='emailbounces.unprocess',
                        permission='emailbounces.unprocess')
        config.add_tailbone_permission('emailbounces', 'emailbounces.unprocess',
                                       "Mark Email Bounce as UN-processed")

        # download raw email
        config.add_route('emailbounces.download', '/email-bounces/{uuid}/download')
        config.add_view(cls, attr='download', route_name='emailbounces.download',
                        permission='emailbounces.download')
        config.add_tailbone_permission('emailbounces', 'emailbounces.download',
                                       "Download raw message of Email Bounce")

        cls._defaults(config)


class LinksFieldRenderer(formalchemy.FieldRenderer):

    def render_readonly(self, **kwargs):
        value = self.raw_value
        if not value:
            return 'n/a'
        html = literal('<ul>')
        for link in value:
            html += literal('<li>{0}:&nbsp; <a href="{1}" target="_blank">{2}</a></li>'.format(
                link.type, link.url, link.title))
        html += literal('</ul>')
        return html


def includeme(config):
    EmailBouncesView.defaults(config)
