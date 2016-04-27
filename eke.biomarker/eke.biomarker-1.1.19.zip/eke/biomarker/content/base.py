# encoding: utf-8
# Copyright 2009–2011 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EKE Biomarker: base content implementation.'''

from eke.biomarker import ProjectMessageFactory as _
from eke.biomarker.interfaces import IBiomarker
from eke.knowledge.content import knowledgeobject
from Products.Archetypes import atapi
from Products.ATContentTypes.content.folder import ATFolder
from Products.CMFCore.utils import getToolByName
from zope.interface import implements, directlyProvides
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

predicateURIBase     = 'http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#'
predicateURIBaseEdrn = 'http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#'

QualityAssuredObjectSchema = atapi.Schema((
    atapi.StringField(
        'qaState',
        storage=atapi.AnnotationStorage(),
        
        widget=atapi.StringWidget(
            label=_(u'QA State'),
            
        ),
        predicateURI=predicateURIBase + 'QAState',
    ),
))

PhasedObjectSchema = atapi.Schema((
    atapi.StringField(
        'phase',
        storage=atapi.AnnotationStorage(),
        
        widget=atapi.StringWidget(
            label=_(u'Phase'),
            
        ),
        predicateURI=predicateURIBase + 'Phase',
    ),
))

ResearchedObjectSchema = atapi.Schema((
    atapi.ReferenceField(
        'protocols',
        storage=atapi.AnnotationStorage(),
        enforceVocabulary=True,
        multiValued=True,
        vocabulary_factory=u'eke.study.ProtocolsVocabulary',
        relationship='protocolsResearchingThisObject',
        vocabulary_display_path_bound=-1,
        widget=atapi.ReferenceWidget(
            label=_(u'Protocols & Studies'),
            
        ),
        predicateURI=predicateURIBase + 'referencesStudy',
    ),
    atapi.ReferenceField(
        'publications',
        storage=atapi.AnnotationStorage(),
        enforceVocabulary=True,
        multiValued=True,
        vocabulary_factory=u'eke.publications.PublicationsVocabulary',
        relationship='publicationsAboutThisObject',
        vocabulary_display_path_bound=-1,
        widget=atapi.ReferenceWidget(
            label=_(u'Publications'),
            
        ),
        predicateURI=predicateURIBase + 'referencedInPublication',
    ),
    atapi.ReferenceField(
        'resources',
        storage=atapi.AnnotationStorage(),
        enforceVocabulary=True,
        multiValued=True,
        vocabulary_factory=u'eke.knowledge.ResourcesVocabulary',
        relationship='resourcesRelatedToThisObjec',
        vocabulary_display_path_bound=-1,
        widget=atapi.ReferenceWidget(
            label=_(u'Resources'),
            
        ),
        predicateURI=predicateURIBase + 'referencesResource',
    ),
    atapi.ReferenceField(
        'datasets',
        storage=atapi.AnnotationStorage(),
        enforceVocabulary=True,
        multiValued=True,
        vocabulary_factory=u'eke.ecas.DatasetsVocabulary',
        relationship='datasetsSupportingThisObject',
        vocabulary_display_path_bound=-1,
        widget=atapi.ReferenceWidget(
            label=_(u'Datasets'),
            
        ),
        predicateURI=predicateURIBase + 'AssociatedDataset',
    ),
))

BiomarkerSchema = knowledgeobject.KnowledgeObjectSchema.copy() + ResearchedObjectSchema.copy() + ATFolder.schema.copy() \
    + atapi.Schema((
    atapi.StringField(
        'shortName',
        storage=atapi.AnnotationStorage(),
        
        widget=atapi.StringWidget(
            label=_(u'Short Name'),
            
        ),
        predicateURI=predicateURIBase + 'ShortName',
    ),
    atapi.StringField(
        'hgncName',
        storage=atapi.AnnotationStorage(),
        
        widget=atapi.StringWidget(
            label=_(u'HGNC Name'),
            
        ),
        predicateURI=predicateURIBase + 'HgncName',
    ),
    atapi.LinesField(
        'bmAliases',
        storage=atapi.AnnotationStorage(),
        
        multiValued=True,
        searchable=True,
        widget=atapi.LinesWidget(
            label=_(u'Aliases'),
            
        ),
        predicateURI=predicateURIBase + 'Alias'
    ),
    atapi.LinesField(
        'indicatedBodySystems',
        storage=atapi.AnnotationStorage(),
        
        multiValued=True,
        searchable=True,
        widget=atapi.LinesWidget(
            label=_(u'Indicated Organs'),
            
            visible={'view': 'invisible', 'edit': 'invisible'},
        ),
    ),
    atapi.ComputedField(
        'biomarkerKind',
        searchable=True,
        
        expression='u"Biomarker"',
        modes=('view',),
        widget=atapi.ComputedWidget(
            visible={'edit': 'invisible', 'view': 'invisible'},
        ),
    ),
    atapi.LinesField(
        'accessGroups',
        storage=atapi.AnnotationStorage(),
        required=False,
        multiValued=True,
        widget=atapi.LinesWidget(
            label=_(u'Access Groups'),
            description=_(u'URIs identifying groups that may access this biomarker.'),
        ),
    ),
    atapi.StringField(
        'geneName',
        storage=atapi.AnnotationStorage(),

        widget=atapi.StringWidget(
            label=_(u'Gene Name'),
        ),
        predicateURI=predicateURIBaseEdrn + 'geneName',
    ),
    atapi.StringField(
        'uniProtAC',
        storage=atapi.AnnotationStorage(),

        widget=atapi.StringWidget(
            label=_(u'Uniprot Accession'),
        ),
        predicateURI=predicateURIBaseEdrn+ 'uniprotAccession',
    ),
    atapi.StringField(
        'mutCount',
        storage=atapi.AnnotationStorage(),

        widget=atapi.StringWidget(
            label=_(u'Number of Mutation Sites'),
        ),
        predicateURI=predicateURIBaseEdrn + 'mutationCount',
    ),
    atapi.StringField(
        'pmidCount',
        storage=atapi.AnnotationStorage(),

        widget=atapi.StringWidget(
            label=_(u'Pubmed ID Count'),
        ),
        predicateURI=predicateURIBaseEdrn + 'pubmedIDCount',
    ),
    atapi.StringField(
        'cancerDOCount',
        storage=atapi.AnnotationStorage(),

        widget=atapi.StringWidget(
            label=_(u'CancerDO  Count'),
        ),
        predicateURI=predicateURIBaseEdrn + 'cancerDOCount',
    ),
    atapi.StringField(
        'affProtFuncSiteCount',
        storage=atapi.AnnotationStorage(),

        widget=atapi.StringWidget(
            label=_(u'Affected Protein Function Site Count'),
        ),
        predicateURI=predicateURIBaseEdrn + 'affectedProtFuncSiteCount',
    ),
    atapi.StringField(
        'reshgnc',
        storage=atapi.AnnotationStorage(),

        widget=atapi.StringWidget(
            label=_(u'HGNC'),
        ),
        predicateURI=predicateURIBaseEdrn + 'reshgnc',
    ),
    atapi.StringField(
        'reskegg',
        storage=atapi.AnnotationStorage(),

        widget=atapi.StringWidget(
            label=_(u'KEGG'),
        ),
        predicateURI=predicateURIBaseEdrn + 'reskegg',
    ),
    atapi.StringField(
        'resentrez',
        storage=atapi.AnnotationStorage(),

        widget=atapi.StringWidget(
            label=_(u'Entrez'),
        ),
        predicateURI=predicateURIBaseEdrn + 'resentrez',
    ),
    atapi.StringField(
        'geoprofile',
        storage=atapi.AnnotationStorage(),

        widget=atapi.StringWidget(
            label=_(u'GEO Profiles'),
        ),
        predicateURI=predicateURIBaseEdrn + 'geoprofile',
    ),
    atapi.StringField(
        'geodataset',
        storage=atapi.AnnotationStorage(),

        widget=atapi.StringWidget(
            label=_(u'GEO Datasets'),
        ),
        predicateURI=predicateURIBaseEdrn + 'geodataset',
    ),
    atapi.StringField(
        'ressnp',
        storage=atapi.AnnotationStorage(),

        widget=atapi.StringWidget(
            label=_(u'SNP'),
        ),
        predicateURI=predicateURIBaseEdrn + 'ressnp',
    ),
    atapi.StringField(
        'resgene',
        storage=atapi.AnnotationStorage(),

        widget=atapi.StringWidget(
            label=_(u'Gene'),
        ),
        predicateURI=predicateURIBaseEdrn + 'resgene',
    ),
    atapi.StringField(
        'gwasref',
        storage=atapi.AnnotationStorage(),

        widget=atapi.StringWidget(
            label=_(u'GWAS'),
        ),
        predicateURI=predicateURIBaseEdrn + 'gwasref',
    ),
    atapi.StringField(
        'generef',
        storage=atapi.AnnotationStorage(),

        widget=atapi.StringWidget(
            label=_(u'Gene RefSeq'),
        ),
        predicateURI=predicateURIBaseEdrn + 'generef',
    ),
    atapi.StringField(
        'resuniprot',
        storage=atapi.AnnotationStorage(),

        widget=atapi.StringWidget(
            label=_(u'UniProtKB/Swiss-Prot'),
        ),
        predicateURI=predicateURIBaseEdrn + 'resuniprot',
    ),
    atapi.StringField(
        'proteinref',
        storage=atapi.AnnotationStorage(),

        widget=atapi.StringWidget(
            label=_(u'Protein RefSeq'),
        ),
        predicateURI=predicateURIBaseEdrn + 'proteinref',
    ),
    atapi.StringField(
        'resfda',
        storage=atapi.AnnotationStorage(),

        widget=atapi.StringWidget(
            label=_(u'FDA'),
        ),
        predicateURI=predicateURIBaseEdrn + 'resfda',
    ),
    atapi.StringField(
        'resgenecard',
        storage=atapi.AnnotationStorage(),

        widget=atapi.StringWidget(
            label=_(u'Genecards'),
        ),
        predicateURI=predicateURIBaseEdrn + 'resgenecard',
    )
))

# FIXME: These should probably both be Dublin Core some day:
BiomarkerSchema['title'].predicateURI = predicateURIBase + 'Title'
BiomarkerSchema['description'].predicateURI = predicateURIBase + 'Description'

class Biomarker(ATFolder, knowledgeobject.KnowledgeObject):
    '''Biomarker.'''
    implements(IBiomarker)
    schema               = BiomarkerSchema
    accessGroups         = atapi.ATFieldProperty('accessGroups')
    biomarkerKind        = atapi.ATFieldProperty('biomarkerKind')
    bmAliases            = atapi.ATFieldProperty('bmAliases')
    description          = atapi.ATFieldProperty('description')
    indicatedBodySystems = atapi.ATFieldProperty('indicatedBodySystems')
    protocols            = atapi.ATReferenceFieldProperty('protocols')
    publications         = atapi.ATReferenceFieldProperty('publications')
    resources            = atapi.ATReferenceFieldProperty('resources')
    datasets             = atapi.ATReferenceFieldProperty('datasets')
    shortName            = atapi.ATFieldProperty('shortName')
    hgncName             = atapi.ATFieldProperty('hgncName')
    geneName             = atapi.ATFieldProperty('geneName')
    uniProtAC            = atapi.ATFieldProperty('uniProtAC')
    mutCount             = atapi.ATFieldProperty('mutCount')
    pmidCount            = atapi.ATFieldProperty('pmidCount')
    cancerDOCount        = atapi.ATFieldProperty('cancerDOCount')
    affProtFuncSiteCount = atapi.ATFieldProperty('affProtFuncSiteCount')
    reshgnc              = atapi.ATFieldProperty('reshgnc')
    reskegg              = atapi.ATFieldProperty('reskegg')
    resentrez            = atapi.ATFieldProperty('resentrez')
    geoprofile           = atapi.ATFieldProperty('geoprofile')
    geodataset           = atapi.ATFieldProperty('geodataset')
    ressnp               = atapi.ATFieldProperty('ressnp')
    gwasref              = atapi.ATFieldProperty('gwasref')
    resgene              = atapi.ATFieldProperty('resgene')
    generef              = atapi.ATFieldProperty('generef')
    resuniprot           = atapi.ATFieldProperty('resuniprot')
    proteinref           = atapi.ATFieldProperty('proteinref')
    resfda               = atapi.ATFieldProperty('resfda')
    resgenecard          = atapi.ATFieldProperty('resgenecard')

    def _computeIndicatedBodySystems(self):
        return [i.capitalize() for i in self.objectIds()]
    def updatedIndicatedBodySystems(self):
        self.indicatedBodySystems = self._computeIndicatedBodySystems()
    def SearchableText(self):
        txt = super(Biomarker, self).SearchableText()
        certifications = ''
        for objID, obj in self.contentItems():
            if obj.cliaCertification:
                certifications += 'CLIA ' * 5
            if obj.fdaCertification:
                certifications += 'FDA ' * 20
        return certifications + txt

def BiomarkerVocabularyFactory(context):
    '''Yield a vocabulary for biomarkers.'''
    catalog = getToolByName(context, 'portal_catalog')
    # TODO: filter by review_state?
    results = catalog(object_provides=IBiomarker.__identifier__, sort_on='sortable_title')
    terms = [SimpleVocabulary.createTerm(i.UID, i.UID, i.Title.decode('utf-8')) for i in results]
    return SimpleVocabulary(terms)
directlyProvides(BiomarkerVocabularyFactory, IVocabularyFactory)

def BodySystemUpdater(context, event):
    context.updatedIndicatedBodySystems()
    # We need to update the indicatedBodySystems index, but also SearchableText for certifications,
    # so just do the whole object.
    context.reindexObject()

def IndicatedOrgansVocabularyFactory(context):
    '''Get a vocab for indicated organs'''
    catalog = getToolByName(context, 'portal_catalog')
    results = catalog.uniqueValuesFor('indicatedBodySystems')
    return SimpleVocabulary.fromItems([(i.decode('utf-8'), i.decode('utf-8')) for i in results])
directlyProvides(IndicatedOrgansVocabularyFactory, IVocabularyFactory)    
