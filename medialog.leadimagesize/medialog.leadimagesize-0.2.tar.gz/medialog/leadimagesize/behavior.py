# -*- coding: utf-8 -*-
#from plone.dexterity.interfaces import IDexterityContent
from plone.supermodel import model
from zope.interface import provider
from zope import schema
from zope.i18nmessageid import MessageFactory
from plone.autoform.interfaces import IFormFieldProvider

from plone import api

_ = MessageFactory('medialog.leadimagesizes')

@provider(IFormFieldProvider)
class ICustomSize(model.Schema):
    """ A field where you can set the size for lead image"""
    
    leadsize = schema.Choice(
        title = _("label_leadimagesize", default=u"Image Size"),
        description = _("help_leadimagesize",
                      default="Choose Size"),
        vocabulary='medialog.leadimagesize.LeadImageSizeVocabulary',
        defaultFactory=lambda: api.portal.get_registry_record('medialog.leadimagesize.interfaces.ILeadImageSizeSettings.leadsize') ,
    )

