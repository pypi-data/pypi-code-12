# -*- coding: utf-8 -*-
"""MLS Agency Contact Info Settings Control Panel."""

# zope imports
from plone.app.registry.browser import controlpanel
from plone.registry.interfaces import IRegistry
from z3c.form import field
from zope.component import getUtility
from zope.interface import implementer

# local imports
from plone.mls.listing.i18n import _
from plone.mls.listing.interfaces import (
    IMLSAgencyContactInformation,
    IMLSAgencyContactInfoSettingsEditForm,
    IMLSUISettings,
)


class SelfHealingRegistryEditForm(controlpanel.RegistryEditForm):
    """Registers the schema if an error occured."""

    def getContent(self):
        registry = getUtility(IRegistry)
        try:
            return registry.forInterface(
                self.schema,
                prefix=self.schema_prefix,
            )
        except KeyError:
            self.ignoreContext = True
            self.fields = field.Fields()
            registry.registerInterface(self.schema)
            self.status = _(
                u'Registry has been updated. Please reload this page.'
            )
            return None


@implementer(IMLSAgencyContactInfoSettingsEditForm)
class MLSAgencyContactInfoSettingsEditForm(SelfHealingRegistryEditForm):
    """MLS Agency Contact Info Settings Form."""

    schema = IMLSAgencyContactInformation
    label = u''

    def updateFields(self):
        super(MLSAgencyContactInfoSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(MLSAgencyContactInfoSettingsEditForm, self).updateWidgets()


class MLSAgencyContactInfoSettingsControlPanel(
        controlpanel.ControlPanelFormWrapper):
    """MLS Agency Contact Info Settings Control Panel."""

    form = MLSAgencyContactInfoSettingsEditForm


class MLSUISettingsEditForm(SelfHealingRegistryEditForm):
    """MLS UI Settings Form."""

    schema = IMLSUISettings
    label = u''

    def updateFields(self):
        super(MLSUISettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(MLSUISettingsEditForm, self).updateWidgets()


class MLSUISettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    """MLS UI Settings Control Panel."""

    form = MLSUISettingsEditForm
