# encoding: utf-8
# Copyright 2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Interface for a generic group index.'''

from edrnsite.collaborations import PackageMessageFactory as _
from eke.site.interfaces import IPerson
from zope import schema
from zope.interface import Interface

class IGroupSpaceIndex(Interface):
    '''A group space index provides the view and discussion for a group.'''
    chair = schema.Object(
        title=_(u'Chair'),
        description=_(u'The person in charge of this group.'),
        required=False,
        schema=IPerson
    )
    coChair = schema.Object(
        title=_(u'Co-Chair'),
        description=_(u'The assistant to the person in charge of this group.'),
        required=False,
        schema=IPerson
    )
    members = schema.List(
        title=_(u'Members'),
        description=_(u'Members of this group.'),
        required=False,
        value_type=schema.Object(
            title=_(u'Member'),
            description=_(u'A member of this group.'),
            schema=IPerson
        )
    )
