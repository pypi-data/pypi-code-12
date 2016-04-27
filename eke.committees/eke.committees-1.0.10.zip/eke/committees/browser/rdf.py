# encoding: utf-8
# Copyright 2010 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''
EKE Committees: RDF ingest for Committee Folders and their Committees.
'''

from Acquisition import aq_inner
from edrnsite.collaborations.interfaces import IGroupSpace
from eke.knowledge import dublincore
from eke.knowledge.browser.rdf import KnowledgeFolderIngestor, CreatedObject, Results
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.CMFCore.utils import getToolByName
from rdflib import URIRef, ConjunctiveGraph, URLInputSource
from zope.component import getUtility
from urllib2 import urlopen

# RDF predicates
_abbrevNamePredicateURI    = URIRef(u'http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#abbreviatedName')
_chairPredicateURI         = URIRef(u'http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#chair')
_coChairPredicateURI       = URIRef(u'http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#coChair')
_committeeTypePredicateURI = URIRef(u'http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#committeeType')
_consultantPredicateURI    = URIRef(u'http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#consultant')
_dcTitleURI                = URIRef(dublincore.TITLE_URI)
_memberPredicateURI        = URIRef(u'http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#member')

# Collaborative group's interface
_collabGroup = 'edrnsite.collaborations.interfaces.collaborativegroupindex.ICollaborativeGroupIndex'

class CreatedObjectWrapper(object):
    def __init__(self, obj):
        self.obj = obj
        self.title = obj.title
        self.identifier = obj.id
    def absolute_url(self):
        return self.obj.absolute_url()


class CommitteeFolderIngestor(KnowledgeFolderIngestor):
    '''Committee Folder ingestion.'''
    def getSummaryData(self,  source):
        jsonlines = urlopen(source)
        json = ""
        for line in jsonlines:
            json += line
        return json

    def __call__(self, rdfDataSource=None):
        context = aq_inner(self.context)
        if rdfDataSource is None: rdfDataSource = context.rdfDataSource
        siteSumDataSource = context.siteSumDataSource
        context.dataSummary = self.getSummaryData(siteSumDataSource)

        normalize = getUtility(IIDNormalizer).normalize
        catalog = getToolByName(context, 'portal_catalog')
        graph = ConjunctiveGraph()
        graph.parse(URLInputSource(rdfDataSource))
        statements = self._parseRDF(graph)
        createdObjects, warnings = [], []
        for uri, predicates in statements.iteritems():
            if _dcTitleURI not in predicates: continue
            committeeTypes = [unicode(i) for i in predicates.get(_committeeTypePredicateURI, [])]
            if len(committeeTypes) > 0 and committeeTypes[0] == u'Collaborative Group':
                # These are handled by edrnsite.collaborations directly, so don't create Group Spaces
                continue
            title = unicode(predicates[_dcTitleURI][0])
            results = catalog(
                Title=title,
                object_provides=IGroupSpace.__identifier__,
                path=dict(query='/'.join(context.getPhysicalPath()), depth=1)
            )
            objectID = normalize(title)
            if len(results) == 1 or objectID in context.keys():
                # Existing group space, update it
                if objectID in context.keys():
                    gs = context[objectID]
                else:
                    gs = results[0].getObject()
                oldID = gs.id
                self.updateGroupSpace(gs, predicates, catalog)
                newID = normalize(gs.title)
                if oldID != newID:
                    # Need to update object ID too
                    gs.setId(newID)
                gs.reindexObject()
                createdObjects.append(CreatedObject(CreatedObjectWrapper(gs)))
            else:
                if len(results) > 1:
                    # WTF? We got multiple group spaces with the same title?  Nuke 'em all because something's fubared.
                    context.manage_delObjects([gs.id for gs in results])
                # Brand new Group Space
                gs = context[context.invokeFactory('Group Space', objectID)]
                self.updateGroupSpace(gs, predicates, catalog)
                gs.reindexObject()
                createdObjects.append(CreatedObject(CreatedObjectWrapper(gs)))
        self.updateCollaborativeGroups(statements, catalog, normalize)
        self.objects = createdObjects
        self._results = Results(self.objects, warnings=warnings)

        return self.renderResults()
    def updateCollaborativeGroups(self, statements, catalog, normalizer):
        '''Update members of any matching collaborative groups'''
        portal = getToolByName(catalog, 'portal_url').getPortalObject()
        if 'collaborative-groups' in portal.keys():
            collaborativeGroups = portal['collaborative-groups']
        else:
            collaborativeGroups = portal[portal.invokeFactory('Collaborations Folder', 'collaborative-groups')]
            collaborativeGroups.setTitle(u'Collaborative Groups')
            collaborativeGroups.setDescription(u'Collaborative groups are people that work together.')
        for uri, predicates in statements.iteritems():
            committeeTypes = [unicode(i) for i in predicates.get(_committeeTypePredicateURI, [])]
            if len(committeeTypes) == 0 or committeeTypes[0] != u'Collaborative Group': continue
            title = unicode(predicates[_dcTitleURI][0])
            objID = normalizer(title)
            if objID in collaborativeGroups.keys():
                cb = collaborativeGroups[objID]
                index = cb['index_html']
            else:
                cb = collaborativeGroups[collaborativeGroups.invokeFactory('Collaborative Group', objID)]
                index = cb[cb.invokeFactory('Collaborative Group Index', 'index_html')]
                cb.setTitle(title)
                index.setTitle(title)
            members = []
            chairs = predicates.get(_chairPredicateURI, [])
            if len(chairs) >= 1:
                index.setChair(self.getPersonUID(chairs[0], catalog))
                members.extend(chairs[1:])
            coChairs = predicates.get(_coChairPredicateURI, [])
            if len(coChairs) >= 1:
                index.setCoChair(self.getPersonUID(coChairs[0], catalog))
                members.extend(coChairs[1:])
            members.extend(predicates.get(_consultantPredicateURI, []))
            members.extend(predicates.get(_memberPredicateURI, []))
            index.setMembers([self.getPersonUID(i, catalog) for i in members])

            cb.reindexObject()
            index.reindexObject()
    def getPersonUID(self, identifier, catalog=None):
        if not catalog:
            catalog = getToolByName(aq_inner(self.context), 'portal_catalog')
        results = catalog(identifier=unicode(identifier))
        return results[0].UID if len(results) > 0 else None
    def updateGroupSpace(self, groupSpace, predicates, catalog=None):
        if catalog is None: catalog = getToolByName(aq_inner(self.context), 'portal_catalog')
        if 'index_html' in groupSpace.keys():
            index = groupSpace['index_html']
        else:
            index = groupSpace[groupSpace.invokeFactory('Group Space Index', 'index_html')]
        if _dcTitleURI in predicates:
            title = unicode(predicates[_dcTitleURI][0])
            groupSpace.setTitle(title)
            index.setTitle(title)
        if not index.Description():
            description = []
            if _abbrevNamePredicateURI in predicates:
                msg = u'Abbreviated name: %s.' % unicode(predicates[_abbrevNamePredicateURI][0])
                description.append(msg)
            if _committeeTypePredicateURI in predicates:
                msg = u'Committee type: %s.' % unicode(predicates[_committeeTypePredicateURI][0])
                description.append(msg)
            description = u' '.join(description)
            groupSpace.setDescription(description)
            index.setDescription(description)
        members = []
        chairs = predicates.get(_chairPredicateURI, [])
        if len(chairs) >= 1:
            index.setChair(self.getPersonUID(chairs[0], catalog))
            members.extend(chairs[1:])
        coChairs = predicates.get(_coChairPredicateURI, [])
        if len(coChairs) >= 1:
            index.setCoChair(self.getPersonUID(coChairs[0], catalog))
            members.extend(coChairs[1:])
        members.extend(predicates.get(_consultantPredicateURI, []))
        members.extend(predicates.get(_memberPredicateURI, []))
        index.setMembers([self.getPersonUID(i, catalog) for i in members])
