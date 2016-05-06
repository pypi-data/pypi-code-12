from zope.interface import Interface
from z3c.form import interfaces
from zope import schema
from zope.interface import alsoProvides
from plone.directives import form
from medialog.controlpanel.interfaces import IMedialogControlpanelSettingsProvider

from zope.i18nmessageid import MessageFactory

_ = MessageFactory('medialog.leadimagesize')


class ILeadImageSize(Interface):
    """Marker interface for leadimagesize"""


class ILeadImageSizeSettings(form.Schema):
    """Adds settings to medialog.controlpanel
    """

    form.fieldset(
        'leadimage',
        label=_(u'LeadImage'),
        fields=[
             'leadsize',
        ],
     )
    
    leadsize = schema.Choice(
        title = _("label_leadimagesize", default=u"Image Size"),
        description = _("help_leadimagesize",
                      default="Choose Default Image Size"),
        vocabulary='medialog.leadimagesize.LeadImageSizeVocabulary',
        default='mini',
    )

alsoProvides(ILeadImageSizeSettings, IMedialogControlpanelSettingsProvider)