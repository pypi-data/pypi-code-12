# encoding: utf-8
# Copyright 2011 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Highlight implementation'''

from edrnsite.collaborations.config import PROJECTNAME
from edrnsite.collaborations.interfaces import IHighlight
from Products.Archetypes import atapi
from Products.ATContentTypes.content import newsitem, schemata
from zope.interface import implements

HighlightSchema = newsitem.ATNewsItemSchema.copy() + atapi.Schema((
    # No additional fields
))

schemata.finalizeATCTSchema(HighlightSchema, folderish=False, moveDiscussion=True)

class Highlight(newsitem.ATNewsItem):
    '''A highlighted news item.'''
    implements(IHighlight)
    schema      = HighlightSchema
    portal_type = 'Highlight'

atapi.registerType(Highlight, PROJECTNAME)
