# -*- coding: utf-8 -*-

"""
Created on 2016-06-15
:author: Oshane Bailey (b4.oshany@gmail.com)
"""

import colander
import deform
from kotti.views.edit import ContentSchema
from kotti.views.form import AddFormView
from kotti.views.form import EditFormView
from pyramid.view import view_config

from kotti_site_settings import _
from kotti_site_settings.resources import AppSettingsPage


class AppSettingsPageSchema(ContentSchema):
    """ Schema for CustomContent. """
    title = colander.SchemaNode(
        colander.String(),
        title=_(u'Settings for:'),
    )


@view_config(name=AppSettingsPage.type_info.add_view,
             permission=AppSettingsPage.type_info.add_permission,
             renderer='kotti:templates/edit/node.pt')
class AppSettingsPageAddForm(AddFormView):
    """ Form to add a new instance of CustomContent. """

    schema_factory = AppSettingsPageSchema
    add = AppSettingsPage
    item_type = _(u"System Settings")

    def save_success(self, appstruct):
        title = appstruct["title"]
        if not title.lower().endswith("settings"):
            appstruct["title"] = "{} Settings".format(title)
        appstruct["editor_name"] = "{}".format(self.request.user.name)
        return super(AppSettingsPageAddForm, self).save_success(appstruct)


@view_config(name='edit', context=AppSettingsPage, permission='edit',
             renderer='kotti:templates/edit/node.pt')
class AppSettingsPageEditForm(EditFormView):
    """ Form to edit existing CustomContent objects. """

    schema_factory = AppSettingsPageSchema

    def save_success(self, appstruct):
        appstruct["editor_name"] = "{}".format(self.request.user.name)
        return super(AppSettingsPageEditForm, self).save_success(appstruct)
