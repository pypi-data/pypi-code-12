import logging
from zope import component
from zope import interface
from zope import schema
try:
    from zope.component.hooks import getSite
except ImportError:
    #BBB
    from zope.site.hooks import getSite

from plone.registry.interfaces import IRecordModifiedEvent
from plone.app.registry.browser import controlpanel as basepanel
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('collective.js.multizoom')

class IMultizoomPrefs(interface.Interface):
    """Multizoom Prefs"""

    zoom_width = schema.Int(title=_(u'label_zoom_width', default=u'Zoom width'),
                          default=300,
                          required=True)

    zoom_height = schema.Int(title=_(u'label_zoom_height', default=u'Zoom height'),
                          default=300,
                          required=True)

class MultizoomControlPanelForm(basepanel.RegistryEditForm):
    schema = IMultizoomPrefs
    control_panel_view = "@@jquery-multizoom-controlpanel"


class MultizoomControlPanelView(basepanel.ControlPanelFormWrapper):
    form = MultizoomControlPanelForm
    index = ViewPageTemplateFile('controlpanel.pt')
    label = u"Multizoom settings"

