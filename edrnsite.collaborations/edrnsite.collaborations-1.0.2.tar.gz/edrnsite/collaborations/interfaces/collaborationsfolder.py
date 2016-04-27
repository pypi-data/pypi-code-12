# encoding: utf-8
# Copyright 2011 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Interface for a collaborations folder.'''

from edrnsite.collaborations import PackageMessageFactory as _
from zope import schema
from zope.container.constraints import contains
from zope.interface import Interface

class ICollaborationsFolder(Interface):
    '''A collaborations folder contains collaborative groups.'''
    contains('edrnsite.collaborations.interfaces.ICollaborativeGroup')
    title = schema.TextLine(
        title=_(u'Title'),
        description=_(u'The name of this collaborations folder.'),
        required=True,
    )
    description = schema.Text(
        title=_(u'Description'),
        description=_(u'A short summary of this collaborations folder.'),
        required=False,
    )
