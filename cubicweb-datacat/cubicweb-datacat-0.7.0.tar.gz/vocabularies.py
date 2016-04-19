# -*- coding: utf-8 -*-
# copyright 2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-datacat vocabularies (concept schemes)"""

from __future__ import print_function

from os.path import dirname, join

from cubicweb.dataimport import massive_store, stores, ucsvreader
from cubicweb.dataimport.importer import ExtEntity, SimpleImportLog

from cubes.skos.sobjects import import_skos_extentities


DCAT_SCHEMES = [
    (u'ADMS vocabularies',
     u'https://joinup.ec.europa.eu/svn/adms/ADMS_v1.00/ADMS_SKOS_v1.00.rdf'),
    (u'European Frequency Named Authority List',
     u'http://publications.europa.eu/mdr/resource/authority/frequency/skos/frequencies-skos.rdf'),
    (u'European Filetypes Authority Table',
     u'http://publications.europa.eu/mdr/resource/authority/file-type/skos/filetypes-skos.rdf'),
    (u'European Languages Named Authority List',
     u'http://publications.europa.eu/mdr/resource/authority/language/skos/languages-skos.rdf'),
    (u'European Dataset Theme Vocabulary',
     u'http://publications.europa.eu/mdr/resource/authority/data-theme/skos/data-theme-skos.rdf'),
    (u'European Licences Named Authority List',
     u'http://publications.europa.eu/mdr/resource/authority/licence/skos/licences-skos.rdf'),
]

LICENSE_SCHEME = u'http://publications.europa.eu/resource/authority/licence'

ADMS_FRENCH_LABELS = {
    'http://purl.org/adms/assettype/CodeList': u'Liste de codes',
    'http://purl.org/adms/assettype/CoreComponent': u'Composant commun',
    'http://purl.org/adms/assettype/DomainModel': u'Modèle de domaine',
    # 'http://purl.org/adms/assettype/InformationExchangePackageDescription': u'',
    'http://purl.org/adms/assettype/Mapping': u'Correspondance',
    'http://purl.org/adms/assettype/NameAuthorityList': u"Liste de noms d'autorité",
    'http://purl.org/adms/assettype/Ontology': u'Ontologie',
    'http://purl.org/adms/assettype/Schema': u'Schéma',
    'http://purl.org/adms/assettype/ServiceDescription': u"Description d'un service",
    'http://purl.org/adms/assettype/SyntaxEncodingScheme': u"Système d'encodage",
    'http://purl.org/adms/assettype/Taxonomy': u'Taxonomie',
    'http://purl.org/adms/assettype/Thesaurus': u'Thésaurus',
    'http://purl.org/adms/interoperabilitylevel/Legal': u'Légal',
    'http://purl.org/adms/interoperabilitylevel/Organisational': u'Organisationnel',
    'http://purl.org/adms/interoperabilitylevel/Political': u'Politique',
    'http://purl.org/adms/interoperabilitylevel/Semantic': u'Sémantique',
    'http://purl.org/adms/interoperabilitylevel/Technical': u'Technique',
    'http://purl.org/adms/licencetype/Attribution': u'Attribution',
    # 'http://purl.org/adms/licencetype/GrantBack': u'',
    'http://purl.org/adms/licencetype/JurisdictionWithinTheEU': (
        u"Compétence d'une juridiction de l'UE"
    ),
    'http://purl.org/adms/licencetype/KnownPatentEncumbrance': u'Protégé par brevet',
    'http://purl.org/adms/licencetype/NoDerivativeWork': u'Pas de modification',
    'http://purl.org/adms/licencetype/NominalCost': u'Contribution nominale',
    'http://purl.org/adms/licencetype/NonCommercialUseOnly': u"Pas d'utilisation commerciale",
    'http://purl.org/adms/licencetype/OtherRestrictiveClauses': u'Autres clauses restrictives',
    'http://purl.org/adms/licencetype/PublicDomain': u'Domaine public',
    'http://purl.org/adms/licencetype/ReservedNames-Endorsement-OfficialStatus': (
        u'Utilisation du nom ou de la marque interdite'
    ),
    'http://purl.org/adms/licencetype/RoyaltiesRequired': u'Soumis à redevance',
    'http://purl.org/adms/licencetype/UnknownIPR': u'Inconnu',
    'http://purl.org/adms/licencetype/ViralEffect-ShareAlike': u'Partage dans les mêmes conditions',
    'http://purl.org/adms/publishertype/Academia-ScientificOrganisation': (
        u'Académique/Organisation scientifique'
    ),
    'http://purl.org/adms/publishertype/Company': u'Société',
    'http://purl.org/adms/publishertype/IndustryConsortium': u'Consortium industriel',
    'http://purl.org/adms/publishertype/LocalAuthority': u'Collectivité locale',
    'http://purl.org/adms/publishertype/NationalAuthority': u'Administration nationale',
    'http://purl.org/adms/publishertype/NonGovernmentalOrganisation': (
        u'Organisation non gouvernementale'
    ),
    'http://purl.org/adms/publishertype/NonProfitOrganisation': u'Organisation à but non lucratif',
    'http://purl.org/adms/publishertype/PrivateIndividual(s)': u'Individu(s)',
    'http://purl.org/adms/publishertype/RegionalAuthority': u'Autorité régionale',
    'http://purl.org/adms/publishertype/StandardisationBody': u'Organisme de standardisation',
    'http://purl.org/adms/publishertype/SupraNationalAuthority': u'Autorité supra-nationale',
    'http://purl.org/adms/representationtechnique/Archimate': u'Archimate',
    'http://purl.org/adms/representationtechnique/BPMN': u'BPMN',
    'http://purl.org/adms/representationtechnique/CommonLogic': u'Common logic',
    'http://purl.org/adms/representationtechnique/DTD': u'DTD',
    'http://purl.org/adms/representationtechnique/Datalog': u'Datalog',
    'http://purl.org/adms/representationtechnique/Diagram': u'Diagramme',
    'http://purl.org/adms/representationtechnique/Genericode': u'genericode',
    'http://purl.org/adms/representationtechnique/HumanLanguage': u'Langue naturelle',
    'http://purl.org/adms/representationtechnique/IDEF': u'IDEF',
    'http://purl.org/adms/representationtechnique/KIF': u'KIF',
    'http://purl.org/adms/representationtechnique/OWL': u'OWL',
    'http://purl.org/adms/representationtechnique/Prolog': u'Prolog',
    'http://purl.org/adms/representationtechnique/RDFSchema': u'RDFS',
    'http://purl.org/adms/representationtechnique/RIF': u'RIF',
    'http://purl.org/adms/representationtechnique/RelaxNG': u'Relax NG',
    'http://purl.org/adms/representationtechnique/RuleML': u'RuleML',
    'http://purl.org/adms/representationtechnique/SBVR': u'SBVR',
    'http://purl.org/adms/representationtechnique/SKOS': u'SKOS',
    'http://purl.org/adms/representationtechnique/SPARQL': u'SPARQL',
    'http://purl.org/adms/representationtechnique/SPIN': u'SPIN',
    'http://purl.org/adms/representationtechnique/SWRL': u'SWRL',
    'http://purl.org/adms/representationtechnique/Schematron': u'Schematron',
    'http://purl.org/adms/representationtechnique/TopicMaps': u'Carte thématique',
    'http://purl.org/adms/representationtechnique/UML': u'UML',
    'http://purl.org/adms/representationtechnique/WSDL': u'WSDL',
    'http://purl.org/adms/representationtechnique/WSMO': u'WSMO',
    'http://purl.org/adms/representationtechnique/XMLSchema': u'XSD',
    'http://purl.org/adms/status/Completed': u'Terminé',
    'http://purl.org/adms/status/Deprecated': u'Deprécié',
    'http://purl.org/adms/status/UnderDevelopment': u'En développement',
    'http://purl.org/adms/status/Withdrawn': u'Abandonné',
}


def add_source(cnx, name, url):
    return cnx.create_entity('SKOSSource', name=name, url=url)


def datapath(fname):
    return join(dirname(__file__), 'migration', 'data', fname)


def media_types_extentities(media_types=None):
    """Yield ExtEntity objects fetch from parsing IANA CSV files from
    http://www.iana.org/assignments/media-types/media-types.xml.

    If media_types is specified, it should be a list of domain to import.
    Otherwise all domains will be imported.
    """
    iana_uri = 'http://www.iana.org/assignments/media-types/media-types.xml'
    yield ExtEntity('ConceptScheme', iana_uri, {'title': set([u'IANA Media Types'])})
    if media_types is None:
        media_types = ('application', 'audio', 'image', 'message', 'model',
                       'multipart', 'text', 'video')
    for typename in media_types:
        with open(datapath(typename + '.csv')) as f:
            reader = ucsvreader(f, encoding='utf-8', delimiter=',', skipfirst=True)
            concepts = set([])
            for line in reader:
                fulltypename = typename + '/' + line[0]
                if fulltypename in concepts:
                    # Only consider first occurences.
                    continue
                concepts.add(fulltypename)
                yield ExtEntity('Concept', fulltypename, {'in_scheme': set([iana_uri])})
                yield ExtEntity('Label', fulltypename + '_label',
                                {'label': set([fulltypename]),
                                 'language_code': set([u'en']),
                                 'kind': set([u'preferred']),
                                 'label_of': set([fulltypename])})


def media_types_import(cnx, **kwargs):
    """Import of IANA media types concepts from CSV files."""
    import_log = SimpleImportLog('Media Types')
    if cnx.repo.system_source.dbdriver == 'postgres':
        store = massive_store.MassiveObjectStore(cnx)
    else:
        store = stores.NoHookRQLObjectStore(cnx)
    stats, (scheme, ) = import_skos_extentities(
        cnx, media_types_extentities(**kwargs), import_log, store=store,
        raise_on_error=True)
    return stats, scheme
