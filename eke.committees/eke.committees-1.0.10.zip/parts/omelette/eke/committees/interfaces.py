# encoding: utf-8
# Copyright 2010 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EKE Committees: interfaces.
'''

from zope import schema
from zope.container.constraints import contains
from eke.committees import ProjectMessageFactory as _
from eke.knowledge.interfaces import IKnowledgeFolder, IKnowledgeObject
from eke.site.interfaces import IPerson

class ICommitteeFolder(IKnowledgeFolder):
    '''Committee folder.'''
    contains(
        'edrnsite.collaborations.interfaces.IGroupSpace'
        'eke.committees.interfaces.ICommittee',
        'eke.committees.interfaces.ICommitteeFolder',
    )
    dataSummary = schema.TextLine(
        title=_(u'Committee Statistics'),
        description=_(u'Committee statistics.'),
        required=False
    )

class ICommittee(IKnowledgeObject):
    '''Committee.'''
    title = schema.TextLine(
        title=_(u'Title'),
        description=_(u'Name of this committee.'),
        required=True,
    )
    abbreviatedName = schema.TextLine(
        title=_(u'Abbreviated Name'),
        description=_(u'A shorter name for this committee.'),
        required=False,
    )
    committeeType = schema.TextLine(
        title=_(u'Committee Type'),
        description=_(u'What kind of committee this is.'),
        required=False,
    )
    chair = schema.List(
        title=_(u'Chairs'),
        description=_(u'Chairpeople of this committee.'),
        required=False,
        value_type=schema.Object(
            title=_(u'Chair'),
            description=_(u'A single chairperson of this committee.'),
            schema=IPerson
        )
    )
    coChair = schema.List(
        title=_(u'Co-Chairs'),
        description=_(u'Co-chairpeople of this committee.'),
        required=False,
        value_type=schema.Object(
            title=_(u'Co-Chair'),
            description=_(u'A single co-chairperson of this committee.'),
            schema=IPerson
        )
    )
    consultant = schema.List(
        title=_(u'Consultants'),
        description=_(u'Consultants to this committee.'),
        required=False,
        value_type=schema.Object(
            title=_(u'Consultant'),
            description=_(u'A single consultant to this committee.'),
            schema=IPerson
        )
    )
    member = schema.List(
        title=_(u'Members'),
        description=_(u'Members of this committee.'),
        required=False,
        value_type=schema.Object(
            title=_(u'Member'),
            description=_(u'A single member of this committee.'),
            schema=IPerson
        )
    )
