# -*- coding: utf-8 -*-

"""
Created on 2016-06-15
:author: Oshane Bailey (b4.oshany@gmail.com)
"""

from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid import httpexceptions as httpexc

from kotti import DBSession
from kotti_site_settings import _, util
from kotti_site_settings.resources import AppSettings, AppSettingsPage
from kotti_site_settings.fanstatic import css_and_js
from kotti_site_settings.views import BaseView


class BaseSettingViews(BaseView):
    @view_config(name='site-settings', permission='admin', root_only=True,
                 renderer='kotti_site_settings:templates/settings.pt')
    def default_view(self):
        settings = AppSettingsPage.query.all()
        return {
            "settings": settings
        }


@view_defaults(context=AppSettingsPage, permission='admin')
class AppSettingsViews(BaseView):
    """ Views for :class:`kotti_site_settings.resources.CustomContent` """

    @view_config(name='view', permission='admin',
                 renderer='kotti_site_settings:templates/options.pt')
    def default_view(self):
        """ Default view for :class:`kotti_site_settings.resources.CustomContent`

        :result: Dictionary needed to render the template.
        :rtype: dict
        """
        app_settings = AppSettings.query.filter(
            AppSettings.settings_id == self.context.id
        ).all()
        return {
            'app_settings': app_settings
        }

    @view_config(name='update-settings', permission='admin',
                 request_method='POST',
                 renderer='kotti_site_settings:templates/options.pt')
    def process_update_settings(self):
        app_settings = AppSettings.query.filter(
            AppSettings.settings_id == self.context.id
        ).all()
        options = {
            aps.id: aps for aps in app_settings
        }
        for option, value in self.request.params.iteritems():
            if option in options:
                options[option].value = value
                DBSession.add(options[option])
        return httpexc.HTTPFound(location=self.context.path)

    @view_config(name='add-option', permission='admin',
                 request_method='GET',
                 renderer='kotti_site_settings:templates/add_option.pt')
    def add_option(self):
        return {}

    @view_config(name='add-option', permission='admin',
                 request_method='POST',
                 renderer='kotti_site_settings:templates/add_option.pt')
    def process_new_option(self):
        option = self.request.params.get("option", None)
        value = self.request.params.get("value", "")
        if option:
            setting = AppSettings(
                id=util.slugify(option),
                option=option,
                value=value,
                settings_id=self.context.id
            )
            DBSession.add(setting)
            self.request.session.flash(
                "Option has been added",
                "success"
            )
        else:
            self.request.session.flash(
                "No option was given",
                "danger"
            )
        return {}
