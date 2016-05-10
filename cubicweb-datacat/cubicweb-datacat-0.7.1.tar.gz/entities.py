# copyright 2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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

"""cubicweb-datacat entity's classes"""

from os import path
from subprocess import Popen, PIPE, list2cmdline
import sys

from cubicweb import Binary
from cubicweb.predicates import has_related_entities, is_instance
from cubicweb.entities import AnyEntity, adapters
from cubicweb.view import EntityAdapter

from cubes.datacat import (register_catalog_rdf_mapping, register_dataset_rdf_mapping,
                           register_distribution_rdf_mapping, register_publisher_rdf_mapping,
                           register_contact_point_rdf_mapping)
from cubes.file.entities import FileIDownloadableAdapter
from cubes.skos.entities import AbstractRDFAdapter
from cubes.skos.rdfio import unicode_with_language


_ = unicode


def process_type_from_etype(etype):
    """Return the type of data process from etype name"""
    return etype[len('Data'):-len('Process')].lower()


def fspath_from_eid(cnx, eid):
    """Return fspath for an entity with `data` attribute stored in BFSS"""
    rset = cnx.execute('Any fspath(D) WHERE X data D, X eid %(feid)s',
                       {'feid': eid})
    if not rset:
        raise Exception('Could not find file system path for #%d.' % eid)
    return rset[0][0].read()


class Agent(AnyEntity):
    __regid__ = 'Agent'

    def dc_title(self):
        """Return a dc_title built from name and email"""
        title = self.name
        if self.email:
            title += ' <%s>' % self.email
        return title


class Dataset(AnyEntity):
    __regid__ = 'Dataset'

    def dc_title(self):
        """dc_title is either the title or the identifier"""
        return self.title or self.identifier

    @property
    def contact_point(self):
        """Contact point of this Dataset"""
        if self.dataset_contact_point:
            return self.dataset_contact_point[0]


class Distribution(AnyEntity):
    __regid__ = 'Distribution'

    def dc_title(self):
        if self.title:
            return self.title
        elif self.reverse_file_distribution:
            return self.reverse_file_distribution[0].dc_title()
        else:
            return u'{0} #{1}'.format(self.cw_etype, self.eid)


class DownloadableDistributionFile(FileIDownloadableAdapter):

    __select__ = (FileIDownloadableAdapter.__select__
                  & has_related_entities('file_distribution', role='subject'))

    def download_file_name(self):
        name, ext = path.splitext(self.entity.data_name)
        return name[:50] + ext


class DownloadableDistribution(adapters.IDownloadableAdapter):
    """IDownloadable adapter for Distribution entities related to a File."""

    __select__ = (adapters.IDownloadableAdapter.__select__ &
                  has_related_entities('file_distribution', role='object'))

    @property
    def downloadable_file(self):
        """The IDownloadable adapted distribution file."""
        dfile = self.entity.reverse_file_distribution[0]
        return dfile.cw_adapt_to('IDownloadable')

    def download_url(self, **kwargs):
        return self.downloadable_file.download_url(**kwargs)

    def download_content_type(self):
        return self.downloadable_file.download_content_type()

    def download_encoding(self):
        return self.downloadable_file.download_encoding()

    def download_file_name(self):
        return self.downloadable_file.download_file_name()

    def download_data(self):
        return self.downloadable_file.download_data()


class ResourceFeed(AnyEntity):
    __regid__ = 'ResourceFeed'

    @property
    def dataset(self):
        """The Dataset using this ResourceFeed."""
        return self.resource_feed_of[0]

    def scripts_pending_transformation_of(self, inputfile):
        """Yield transformation scripts which have not transformed specified
        `inputfile`.
        """
        rset = self._cw.execute(
            'Any S WHERE RF transformation_script S, RF eid %(rf)s, '
            'NOT EXISTS(TP process_script S, TP process_input_file F, F eid %(f)s, '
            '           X produced_by TP)',
            {'f': inputfile.eid, 'rf': self.eid})
        return rset.entities()

    def scripts_pending_validation_of(self, inputfile):
        """Return the validation script if it has not validated specified
        `inputfile` yet.
        """
        rset = self._cw.execute(
            'Any S WHERE RF validation_script S, RF eid %(rf)s, F eid %(f)s,'
            '            NOT EXISTS(F validated_by VP, VP process_script S)',
            {'f': inputfile.eid, 'rf': self.eid})
        if rset:
            # Cardinality is "?".
            return rset.one()

    def add_transformation_process(self, inputfile, script=None,
                                   depends_on=None):
        """Add a transformation process for `inputfile` using `script`"""
        script = script or self.transformation_script[0]
        if script is None:
            return
        return self._add_process(inputfile, script, 'transformation',
                                 process_depends_on=depends_on)

    def add_validation_process(self, inputfile, script=None):
        """Add a validation process for `inputfile`"""
        script = script or self.validation_script[0]
        if script is None:
            return
        return self._add_process(inputfile, script, 'validation')

    def _add_process(self, inputfile, script, ptype, **kwargs):
        """Launch a script of type `ptype` with `inputfile`"""
        process = self._cw.create_entity(
            'Data%sProcess' % ptype.capitalize(),
            process_for_resourcefeed=self, process_script=script, **kwargs)
        self.info('created %s for resource feed #%d', process, self.eid)
        iprocess = process.cw_adapt_to('IDataProcess')
        # Adding the input file to data process triggers the "start"
        # transition.
        iprocess.add_input(inputfile)
        return process


#
# Adapters
#

# Export to RDF

def fill_graph_with(entity, graph, adapterid):
    """Fill a `graph` using `entity` adaped as `adapterid`."""
    filler = entity.cw_adapt_to(adapterid)
    assert filler, '{0} not adaptable as {1}'.format(entity, adapterid)
    filler.fill(graph)


def add_literal_to_graph(subject_s_uri, property_s_uri, value, graph):
    """Add the following triple to RDF graph: ``(subject_s_uri, property_s_uri, value).``"""
    if value is not None:
        graph.add(graph.uri(subject_s_uri), graph.uri(property_s_uri), value)


def add_uri_to_graph(subject_s_uri, property_s_uri, object_s_uri, graph):
    """Add the following triple to RDF graph: ``(subject_s_uri, property_s_uri, object_s_uri)``."""
    graph.add(graph.uri(subject_s_uri), graph.uri(property_s_uri), graph.uri(object_s_uri))


def add_license_to_graph(license, subject_uri, graph, reg):
    """Add license information to RDF graph for `subject_uri`."""
    reg.register_prefix('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    license_uri = license.cwuri
    add_uri_to_graph(subject_uri, reg.normalize_uri('dcterms:license'), license_uri, graph)
    add_uri_to_graph(license_uri, reg.normalize_uri('rdf:type'),
                     reg.normalize_uri('dcterms:LicenseDocument'), graph)
    add_literal_to_graph(license_uri, reg.normalize_uri('dcterms:title'),
                         license.label(language_code=license._cw.lang), graph)
    if license.license_type:
        concept = license.license_type[0]
        add_concept_to_graph(concept, license_uri, 'dcterms:type', graph, reg)


def add_mediatype_to_graph(concept, subject_uri, rdf_property, graph, reg):
    """Add media_type information to RDF graph for `subject_uri`."""
    reg.register_prefix('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    mediatype_uri = concept.cwuri
    add_uri_to_graph(subject_uri, reg.normalize_uri(rdf_property), mediatype_uri, graph)
    add_uri_to_graph(mediatype_uri, reg.normalize_uri('rdf:type'),
                     reg.normalize_uri('dcterms:MediaTypeOrExtent'), graph)
    add_literal_to_graph(mediatype_uri, reg.normalize_uri('rdf:value'), concept.label(), graph)


def add_language_to_graph(concept, subject_uri, graph, reg):
    """Add language information to RDF graph for `subject_uri`."""
    reg.register_prefix('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    language_uri = concept.cwuri
    add_uri_to_graph(subject_uri, reg.normalize_uri('dcterms:language'), language_uri, graph)
    add_uri_to_graph(language_uri, reg.normalize_uri('rdf:type'),
                     reg.normalize_uri('dcterms:LinguisticSystem'), graph)
    add_literal_to_graph(language_uri, reg.normalize_uri('rdf:value'), concept.label(), graph)


def add_concept_scheme_to_graph(concept_scheme, graph, reg):
    """Add concept scheme to RDF graph related to `subject_uri` with 'relation_uri'."""
    reg.register_prefix('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    reg.register_prefix('skos', 'http://www.w3.org/2004/02/skos/core#')
    reg.register_prefix('dcterms', 'http://purl.org/dc/terms/')
    scheme_uri = concept_scheme.cwuri
    add_uri_to_graph(scheme_uri, reg.normalize_uri('rdf:type'),
                     reg.normalize_uri('skos:ConceptScheme'), graph)
    add_literal_to_graph(scheme_uri, reg.normalize_uri('dcterms:title'), concept_scheme.title,
                         graph)


def add_concept_to_graph(concept, subject_uri, relation_uri, graph, reg):
    """Add concept to RDF graph related to `subject_uri` with 'relation_uri'."""
    reg.register_prefix('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    reg.register_prefix('skos', 'http://www.w3.org/2004/02/skos/core#')
    concept_uri = concept.cwuri
    add_uri_to_graph(subject_uri, reg.normalize_uri(relation_uri), concept_uri, graph)
    add_uri_to_graph(concept_uri, reg.normalize_uri('rdf:type'), reg.normalize_uri('skos:Concept'),
                     graph)
    add_uri_to_graph(concept_uri, reg.normalize_uri('skos:inScheme'), concept.in_scheme[0].cwuri,
                     graph)
    for label in concept.preferred_label:
        add_literal_to_graph(concept_uri, reg.normalize_uri('skos:prefLabel'),
                             unicode_with_language(label.label, label.language_code), graph)


def add_concept_literal_to_graph(concept, subject_uri, relation_uri, graph, reg):
    """Add concept's label to RDF graph related to `subject_uri` with 'relation_uri'."""
    reg.register_prefix('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    reg.register_prefix('skos', 'http://www.w3.org/2004/02/skos/core#')
    label = concept.label(language_code=concept._cw.lang)
    add_literal_to_graph(subject_uri, reg.normalize_uri(relation_uri), label, graph)


class DataCatalogRDFAdapter(AbstractRDFAdapter):
    """Adapt DataCatalog entities to RDF using DCAT vocabulary."""
    __regid__ = 'RDFPrimary'
    __select__ = AbstractRDFAdapter.__select__ & is_instance('DataCatalog')

    register_rdf_mapping = staticmethod(register_catalog_rdf_mapping)

    def fill(self, graph):
        super(DataCatalogRDFAdapter, self).fill(graph)
        reg = self.registry
        reg.register_prefix('foaf', 'http://xmlns.com/foaf/0.1/')
        catalog_uri = self.entity.absolute_url()
        for agent in self.entity.catalog_publisher:
            fill_graph_with(agent, graph, self.__regid__)
        # Export license.
        for license in self.entity.license:
            add_license_to_graph(license, catalog_uri, graph, reg)
        # Export homepage attribute as an RDF resource
        if self.entity.homepage:
            add_uri_to_graph(catalog_uri, reg.normalize_uri('foaf:homepage'), self.entity.homepage,
                             graph)
        # Export languages
        for language in self.entity.language:
            fill_graph_with(language, graph, self.__regid__)
            add_language_to_graph(language, catalog_uri, graph, reg)
        # Export concept scheme
        for scheme in self.entity.theme_taxonomy:
            add_concept_scheme_to_graph(scheme, graph, reg)
            add_uri_to_graph(catalog_uri, reg.normalize_uri('dcat:themeTaxonomy'), scheme.cwuri,
                             graph)


class DatasetRDFAdapter(AbstractRDFAdapter):
    """Adapt Dataset entities to RDF using DCAT vocabulary."""
    __regid__ = 'RDFPrimary'
    __select__ = AbstractRDFAdapter.__select__ & is_instance('Dataset')

    register_rdf_mapping = staticmethod(register_dataset_rdf_mapping)

    def fill(self, graph):
        super(DatasetRDFAdapter, self).fill(graph)
        reg = self.registry
        dataset_uri = self.entity.absolute_url()
        # Export comma-separated keyword attribute as multiple RDF resources
        if self.entity.keyword:
            for keyword in self.entity.keyword.split(u','):
                add_literal_to_graph(dataset_uri, reg.normalize_uri('dcat:keyword'),
                                     keyword.strip(), graph)
        # dct:accrualPeriodicity.
        reg.register_prefix('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
        for concept in self.entity.dataset_frequency:
            frequency_uri = concept.cwuri
            add_uri_to_graph(dataset_uri, reg.normalize_uri('dcterms:accrualPeriodicity'),
                             frequency_uri, graph)
            add_uri_to_graph(frequency_uri, reg.normalize_uri('rdf:type'),
                             reg.normalize_uri('dcterms:Frequency'), graph)
            add_literal_to_graph(frequency_uri, reg.normalize_uri('rdf:value'), concept.label(),
                                 graph)
        # dcat:theme
        for concept in self.entity.dcat_theme:
            add_concept_to_graph(concept, dataset_uri, 'dcat:theme', graph, reg)


class DistributionRDFAdapter(AbstractRDFAdapter):
    """Adapt Distribution entities to RDF using DCAT vocabulary."""
    __regid__ = 'RDFPrimary'
    __select__ = AbstractRDFAdapter.__select__ & is_instance('Distribution')

    register_rdf_mapping = staticmethod(register_distribution_rdf_mapping)

    def fill(self, graph):
        super(DistributionRDFAdapter, self).fill(graph)
        reg = self.registry
        distribution_uri = self.entity.absolute_url()
        # Export access_url and download_url attributes as an RDF resource
        if self.entity.access_url:
            add_uri_to_graph(distribution_uri, reg.normalize_uri('dcat:accessURL'),
                             self.entity.access_url, graph)
        if self.entity.download_url:
            add_uri_to_graph(distribution_uri, reg.normalize_uri('dcat:downloadURL'),
                             self.entity.download_url, graph)
        # Export license. Some clients expect license to be on dataset
        for license in self.entity.license:
            add_license_to_graph(license, distribution_uri, graph, reg)
        # Export distribution_format relation if available
        for filetype in self.entity.distribution_format:
            fill_graph_with(filetype, graph, self.__regid__)
            add_mediatype_to_graph(filetype, distribution_uri, 'dcterms:format', graph, reg)
        # Export distribution_media_type if available
        for mediatype in self.entity.distribution_media_type:
            fill_graph_with(mediatype, graph, self.__regid__)
            add_mediatype_to_graph(mediatype, distribution_uri, 'dcat:mediaType', graph, reg)


class AgentRDFAdapter(AbstractRDFAdapter):
    """Adapt Agent entities to foaf:Agent RDF using FOAF vocabulary."""
    __abstract__ = True

    register_rdf_mapping = staticmethod(register_publisher_rdf_mapping)

    def fill(self, graph):
        super(AgentRDFAdapter, self).fill(graph)
        self.fill_email(graph)

    def fill_email(self, graph):
        raise NotImplementedError()


class PublisherRDFAdapter(AgentRDFAdapter):
    """Adapt publisher Agent entities to foaf:Agent RDF using FOAF vocabulary.
    """
    __regid__ = 'RDFPrimary'
    __select__ = (AgentRDFAdapter.__select__ &
                  (has_related_entities('dataset_publisher', 'object') |
                   has_related_entities('catalog_publisher', 'object')))

    register_rdf_mapping = staticmethod(register_publisher_rdf_mapping)

    def fill(self, graph):
        super(PublisherRDFAdapter, self).fill(graph)
        self.fill_publisher_type(graph)

    def fill_publisher_type(self, graph):
        """Export publisher_type relation and delegate to Concept adapter to
        fill object side of the relation.
        """
        if self.entity.publisher_type:
            concept = self.entity.publisher_type[0]
            add_concept_to_graph(concept, self.entity.absolute_url(), 'dcterms:type', graph,
                                 self.registry)

    def fill_email(self, graph):
        """Export email attribute as a owl:Thing RDF resource"""
        reg = self.registry
        reg.register_prefix('foaf', 'http://xmlns.com/foaf/0.1/')
        if self.entity.email:
            add_uri_to_graph(self.entity.absolute_url(), reg.normalize_uri('foaf:mbox'),
                             u'mailto:{0}'.format(self.entity.email), graph)


class ContactPointRDFAdapter(AgentRDFAdapter):
    """Adapt Agent entities to vcard:Kind RDF using vCard vocabulary."""
    __regid__ = 'RDFContactPoint'
    __select__ = (AgentRDFAdapter.__select__ &
                  has_related_entities('dataset_contact_point', 'object'))

    register_rdf_mapping = staticmethod(register_contact_point_rdf_mapping)

    def fill_email(self, graph):
        reg = self.registry
        # Export email attribute as a owl:Thing RDF resource
        reg.register_prefix('vcard', 'http://www.w3.org/2006/vcard/ns#')
        if self.entity.email:
            add_uri_to_graph(self.entity.absolute_url(), reg.normalize_uri('vcard:hasEmail'),
                             u'mailto:{0}'.format(self.entity.email), graph)


class DataCatalogCkanRDFAdapter(AbstractRDFAdapter):
    """Adapt DataCatalog entities to RDF as expected by CKAN."""
    __regid__ = 'RDFCkan'
    __select__ = AbstractRDFAdapter.__select__ & is_instance('DataCatalog')

    register_rdf_mapping = staticmethod(register_catalog_rdf_mapping)

    def fill(self, graph):
        super(self.__class__, self).fill(graph)
        reg = self.registry
        reg.register_prefix('foaf', 'http://xmlns.com/foaf/0.1/')
        catalog_uri = self.entity.absolute_url()
        for agent in self.entity.catalog_publisher:
            fill_graph_with(agent, graph, self.__regid__)
        # Export license.
        for license in self.entity.license:
            add_license_to_graph(license, catalog_uri, graph, reg)
        # Export homepage attribute as an RDF resource
        if self.entity.homepage:
            add_uri_to_graph(catalog_uri, reg.normalize_uri('foaf:homepage'), self.entity.homepage,
                             graph)
        # Export languages
        for language in self.entity.language:
            fill_graph_with(language, graph, 'RDFPrimary')
            add_language_to_graph(language, catalog_uri, graph, reg)
        # Export concept scheme
        for scheme in self.entity.theme_taxonomy:
            add_concept_scheme_to_graph(scheme, graph, reg)
            add_uri_to_graph(catalog_uri, reg.normalize_uri('dcat:themeTaxonomy'), scheme.cwuri,
                             graph)


class DatasetCkanRDFAdapter(AbstractRDFAdapter):
    """Adapt Dataset entities to RDF as expected by CKAN."""
    __regid__ = 'RDFCkan'
    __select__ = AbstractRDFAdapter.__select__ & is_instance('Dataset')

    register_rdf_mapping = staticmethod(register_dataset_rdf_mapping)

    def fill(self, graph):
        super(self.__class__, self).fill(graph)
        reg = self.registry
        dataset_uri = self.entity.absolute_url()
        # Export comma-separated keyword attribute as multiple RDF resources
        if self.entity.keyword:
            for keyword in self.entity.keyword.split(u','):
                add_literal_to_graph(dataset_uri, reg.normalize_uri('dcat:keyword'),
                                     keyword.strip(), graph)
        # dct:accrualPeriodicity.
        reg.register_prefix('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
        for concept in self.entity.dataset_frequency:
            frequency_label = concept.label(concept._cw.lang)
            add_literal_to_graph(dataset_uri, reg.normalize_uri('dcterms:accrualPeriodicity'),
                                 frequency_label, graph)
        # dcat:theme
        for concept in self.entity.dcat_theme:
            add_concept_literal_to_graph(concept, dataset_uri, 'dcat:theme', graph, reg)


class DistributionCkanRDFAdapter(AbstractRDFAdapter):
    """Adapt Distribution entities to RDF as expected by CKAN."""
    __regid__ = 'RDFCkan'
    __select__ = AbstractRDFAdapter.__select__ & is_instance('Distribution')

    register_rdf_mapping = staticmethod(register_distribution_rdf_mapping)

    def fill(self, graph):
        super(self.__class__, self).fill(graph)
        reg = self.registry
        distribution_uri = self.entity.absolute_url()
        # Export access_url and download_url attributes as an RDF resource
        if self.entity.access_url:
            add_uri_to_graph(distribution_uri, reg.normalize_uri('dcat:accessURL'),
                             self.entity.access_url, graph)
        if self.entity.download_url:
            add_uri_to_graph(distribution_uri, reg.normalize_uri('dcat:downloadURL'),
                             self.entity.download_url, graph)
        # Export license. Some clients expect license to be on dataset
        for license in self.entity.license:
            add_license_to_graph(license, distribution_uri, graph, reg)
        # Export distribution_format relation if available
        for filetype in self.entity.distribution_format:
            add_literal_to_graph(distribution_uri, reg.normalize_uri('dcterms:format'),
                                 filetype.label(), graph)
        # Export distribution_media_type if available
        for mediatype in self.entity.distribution_media_type:
            add_literal_to_graph(distribution_uri, reg.normalize_uri('dcat:mediaType'),
                                 mediatype.label(), graph)


class PublisherCkanRDFAdapter(AgentRDFAdapter):
    """Adapt publisher Agent entities to RDF as expected by CKAN."""

    __regid__ = 'RDFCkan'
    __select__ = (AgentRDFAdapter.__select__ &
                  (has_related_entities('dataset_publisher', 'object') |
                   has_related_entities('catalog_publisher', 'object')))

    register_rdf_mapping = staticmethod(register_publisher_rdf_mapping)

    def fill(self, graph):
        super(self.__class__, self).fill(graph)
        self.fill_publisher_type(graph)

    def fill_publisher_type(self, graph):
        """Export publisher_type relation and delegate to Concept adapter to
        fill object side of the relation.
        """
        if self.entity.publisher_type:
            concept = self.entity.publisher_type[0]
            add_concept_literal_to_graph(concept, self.entity.absolute_url(), 'dcterms:type', graph,
                                         self.registry)

    def fill_email(self, graph):
        """Export email attribute as a owl:Thing RDF resource"""
        reg = self.registry
        reg.register_prefix('foaf', 'http://xmlns.com/foaf/0.1/')
        if self.entity.email:
            add_uri_to_graph(self.entity.absolute_url(), reg.normalize_uri('foaf:mbox'),
                             u'mailto:{0}'.format(self.entity.email), graph)


# Other adapters

class DataProcessAdapter(EntityAdapter):
    """Interface for data processes"""
    __regid__ = 'IDataProcess'
    __select__ = (EntityAdapter.__select__ &
                  is_instance('DataTransformationProcess',
                              'DataValidationProcess'))

    @property
    def process_type(self):
        """The type of data process"""
        return process_type_from_etype(self.entity.cw_etype)

    def state_name(self, name):
        """Return the full workflow state name given a short name"""
        wfs = u'wfs_dataprocess_' + name
        wf = self.entity.cw_adapt_to('IWorkflowable').current_workflow
        if wf.state_by_name(wfs) is None:
            raise ValueError('invalid state name "%s"' % name)
        return wfs

    def tr_name(self, name):
        """Return the full workflow transition name given a short name"""
        wft = u'wft_dataprocess_' + name
        wf = self.entity.cw_adapt_to('IWorkflowable').current_workflow
        if wf.transition_by_name(wft) is None:
            raise ValueError('invalid transition name "%s"' % name)
        return wft

    def fire_workflow_transition(self, trname, **kwargs):
        """Fire transition identified by *short* name `trname` of the
        underlying workflowable entity.
        """
        tr = self.tr_name(trname)
        iwf = self.entity.cw_adapt_to('IWorkflowable')
        return iwf.fire_transition(tr, **kwargs)

    @property
    def process_script(self):
        """The process script attached to entity"""
        if self.entity.process_script:
            assert len(self.entity.process_script) == 1  # schema
            return self.entity.process_script[0]

    def add_input(self, inputfile):
        """Add an input file to the underlying data process"""
        self.entity.cw_set(process_input_file=inputfile)

    def build_output(self, inputfile, data, **kwargs):
        """Return an ouput File produced from `inputfile` with `data` as
        content.
        """
        return self._cw.create_entity('File', data=Binary(data),
                                      data_name=inputfile.data_name,
                                      data_format=inputfile.data_format,
                                      produced_by=self.entity, **kwargs)

    def execute_script(self, inputfile):
        """Execute script in a subprocess using ``inputfile``.

        Eventually set process output file and return subprocess return
        code and subprocess stderr.
        """
        datapath = fspath_from_eid(self._cw, inputfile.eid)
        script = self.process_script
        scriptpath = fspath_from_eid(self._cw, script.implemented_by[0].eid)
        cmdline = [sys.executable, scriptpath, datapath]
        proc = Popen(cmdline, stdout=PIPE, stderr=PIPE)
        self.info('starting subprocess with pid %s: %s',
                  proc.pid, list2cmdline(cmdline))
        stdoutdata, stderrdata = proc.communicate()
        if proc.returncode:
            self.info('subprocess terminated abnormally (exit code %d)',
                      proc.returncode)
        if self.process_type == 'transformation':
            if stdoutdata:
                feid = self.build_output(inputfile, stdoutdata).eid
                self.info(
                    'created File #%d from input file #%d and script #%d',
                    feid, inputfile.eid, self.process_script.eid)
            else:
                # XXX raise?
                self.info('no standard output produced by Script #%d',
                          script.eid)
        return proc.returncode, unicode(stderrdata, errors='ignore')

    def finalize(self, returncode, stderr):
        """Finalize a data process firing the proper transition."""
        if returncode:
            self.fire_workflow_transition('error', comment=stderr)
        else:
            self.fire_workflow_transition('complete', comment=stderr)
