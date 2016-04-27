# encoding: utf-8
# Copyright 2011–2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Collaborative Group index implementation'''

from Acquisition import aq_inner, aq_parent
from edrnsite.collaborations import PackageMessageFactory as _
from edrnsite.collaborations.config import PROJECTNAME
from edrnsite.collaborations.interfaces import ICollaborativeGroupIndex
from groupspaceindex import GroupSpaceIndex, GroupSpaceIndexSchema
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from Products.CMFCore.utils import getToolByName
from zope.interface import implements

CollaborativeGroupIndexSchema = GroupSpaceIndexSchema.copy() + atapi.Schema((
    atapi.ReferenceField(
        'biomarkers',
        storage=atapi.AnnotationStorage(),
        enforceVocabulary=True,
        multiValued=True,
        vocabulary_factory=u'eke.biomarker.BiomarkersVocabulary',
        relationship='biomarkersThisGroupLikes',
        vocabulary_display_path_bound=-1,
        widget=atapi.ReferenceWidget(
            label=_(u'Biomarkers'),
            description=_(u'Biomarkers of which this collaborative group is fond.'),
        ),
    ),
    atapi.ReferenceField(
        'protocols',
        storage=atapi.AnnotationStorage(),
        enforceVocabulary=True,
        multiValued=True,
        vocabulary_factory=u'eke.study.ProtocolsVocabulary',
        relationship='protocolsExecutedByThisGroup',
        vocabulary_display_path_bound=-1,
        widget=atapi.ReferenceWidget(
            label=_(u'Protocols & Studies'),
            description=_(u'Protocols and studies that are executed (and studied) by this collaborative group.'),
        ),
    ),
    atapi.ReferenceField(
        'datasets',
        storage=atapi.AnnotationStorage(),
        enforceVocabulary=True,
        multiValued=True,
        vocabulary_factory=u'eke.ecas.DatasetsVocabulary',
        relationship='datasetsPreferredByThisGroup',
        vocabulary_display_path_bound=-1,
        widget=atapi.ReferenceWidget(
            label=_(u'Datasets'),
            description=_(u'Datasets of interest to this collaborative group.'),
        ),
    ),
    atapi.ReferenceField(
        'projects',
        storage=atapi.AnnotationStorage(),
        enforceVocabulary=True,
        multiValued=True,
        vocabulary_factory=u'eke.study.TeamProjectsVocabulary',
        relationship='teamsThisGroupIsOn',
        vocabulary_display_path_bound=-1,
        widget=atapi.ReferenceWidget(
            label=_(u'Projects'),
            description=_(u'Team projects (which are just special protocols) of which this collaborative group is part.'),
        ),
    ),
))

schemata.finalizeATCTSchema(CollaborativeGroupIndexSchema, folderish=False, moveDiscussion=True)

class CollaborativeGroupIndex(GroupSpaceIndex):
    '''A collaborative group'''
    implements(ICollaborativeGroupIndex)
    schema      = CollaborativeGroupIndexSchema
    portal_type = 'Collaborative Group Index'
    biomarkers  = atapi.ATReferenceFieldProperty('biomarkers')
    datasets    = atapi.ATReferenceFieldProperty('datasets')
    projects    = atapi.ATReferenceFieldProperty('projects')
    protocols   = atapi.ATReferenceFieldProperty('protocols')

atapi.registerType(CollaborativeGroupIndex, PROJECTNAME)

def updateDatasets(obj, event):
    '''Set the ECAS datasets to point to their corresponding Collaborative Group'''
    if not ICollaborativeGroupIndex.providedBy(obj): return
    factory = getToolByName(obj, 'portal_factory')
    if factory.isTemporary(obj): return
    container = aq_parent(aq_inner(obj))
    myUID = container.UID()
    myTitle = container.Title()
    for dataset in obj.datasets:
        dataset.collaborativeGroupUID = myUID
        dataset.collaborativeGroup = myTitle
        dataset.reindexObject(idxs=['collaborativeGroupUID'])
