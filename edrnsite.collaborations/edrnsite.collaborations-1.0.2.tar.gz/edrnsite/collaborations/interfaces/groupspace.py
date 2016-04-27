# encoding: utf-8
# Copyright 2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Interface for a group space'''

from edrnsite.collaborations import PackageMessageFactory as _
from zope import schema
from zope.container.constraints import contains
from zope.interface import Interface

class IGroupSpace(Interface):
    '''A group space is a place for members of a group to share stuff.'''
    contains('edrnsite.collaborations.interfaces.IGroupSpaceIndex')
    title = schema.TextLine(
        title=_(u'Title'),
        description=_(u'The name of this group.'),
        required=True,
    )
    description = schema.Text(
        title=_(u'Description'),
        description=_(u'A short summary of this group.'),
        required=False,
    )
    updateNotifications = schema.Bool(
        title=_(u'Update Notifications'),
        description=_(u'Enable notifying members (by email) of updates to this group.'),
        required=False,
    )
