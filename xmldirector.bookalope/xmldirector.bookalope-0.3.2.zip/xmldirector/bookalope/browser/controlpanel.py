# -*- coding: utf-8 -*-


################################################################
# xmldirector.Bookalope
# (C) 2016,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

from plone.app.registry.browser import controlpanel

from xmldirector.bookalope.interfaces import IBookalopeSettings
from xmldirector.bookalope.i18n import MessageFactory as _


class BookalopeSettingsEditForm(controlpanel.RegistryEditForm):

    schema = IBookalopeSettings
    label = _(u'Bookalope Policy settings')
    description = _(u'')

    def updateFields(self):
        super(BookalopeSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(BookalopeSettingsEditForm, self).updateWidgets()


class BookalopeSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = BookalopeSettingsEditForm
