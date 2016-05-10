# copyright 2014-2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-datacat views/forms/actions/components for web ui"""

from copy import deepcopy
from os.path import dirname, join
import json
import re
import urlparse

from logilab.mtconverter import xml_escape

from cubicweb import tags
from cubicweb.predicates import (adaptable, has_related_entities, is_instance,
                                 one_line_rset, score_entity)
from cubicweb.utils import json_dumps
from cubicweb.web import action, component, facet as cwfacet, formwidgets as fw
from cubicweb.web.views import (actions, ajaxcontroller, baseviews, ibreadcrumbs, json as jsonviews,
                                navigation, uicfg)
from cubicweb.view import EntityView

from cubes.relationwidget import views as rwdg
from cubes.skos import rdfio
from cubes.skos.views import rdf as rdfviews

_ = unicode

abaa = uicfg.actionbox_appearsin_addmenu
afs = uicfg.autoform_section
affk = uicfg.autoform_field_kwargs
pvdc = uicfg.primaryview_display_ctrl
pvs = uicfg.primaryview_section


def build_selectable_uicfg(rtag, select):
    """Return a copy of uicfg `rtag` with `select` set."""
    copy = deepcopy(rtag)
    copy.__module__ = __name__
    copy.__select__ = select
    return copy


def _autocomplete_widget(fname):
    return fw.LazyRestrictedAutoCompletionWidget(
        attrs={'placeholder': _(u"Start to type your choice: you'll be presented a list of "
                                u"matching terms"),
               'size': 82},
        autocomplete_initfunc=fname,
        autocomplete_settings={'limit': 100, 'delay': 300},
    )


def search_in_scheme(req, scheme_uri):
    """Query ConceptScheme with `scheme_uri` for a Label matching `q` term
    found in request's form.
    """
    term = req.form['q']
    limit = req.form.get('limit', 50)
    lang = req.lang
    qs = ('DISTINCT Any X LIMIT {0} '
          'WHERE X in_scheme S, S cwuri %(scheme)s, L label_of X, L label LL,'
          '      L label ILIKE %(term)s'.format(limit))
    args = {'scheme': scheme_uri, 'term': u'%%%s%%' % term}
    return [{'value': concept.eid, 'label': concept.label(language_code=lang)}
            for concept in req.execute(qs, args).entities()]


class NoRedirectAddRelatedActions(actions.AddRelatedActions):
    """Override 'addrelated' action to avoid redirection to the parent entity."""

    __select__ = (actions.AddRelatedActions.__select__ &
                  is_instance('Agent', 'DataCatalog', 'Dataset', 'Distribution'))

    def redirect_params(self, *args, **kwargs):
        return {}


class WorkflowableEntityOutOfContextView(baseviews.OutOfContextView):
    """Out of context view showing workflow state"""

    __select__ = baseviews.OutOfContextView.__select__ & adaptable('IWorkflowable')

    def cell_call(self, row, col, **kwargs):
        self.w(u'<div style="margin-top: 1px;" class="clearfix">')
        super(WorkflowableEntityOutOfContextView, self).cell_call(row, col, **kwargs)
        entity = self.cw_rset.get_entity(row, col)
        iwf = entity.cw_adapt_to('IWorkflowable')
        self.w(tags.span(iwf.printable_state, klass='badge pull-right'))
        self.w(u'</div>')


#
# RDF views
#

class DatasetDCATRDFView(rdfviews.RDFPrimaryView):
    """RDF view for Dataset entities, outputting complete information about
    catalog, distributions and agents.

    This is mainly useful for clients who *do not follow URIs* to gather information about related
    resources and expect all information at one URL (eg. CKAN).
    """

    __regid__ = 'dcat.rdf.complete'
    __select__ = rdfviews.RDFPrimaryView.__select__ & is_instance('Dataset')

    def entity_call(self, entity, graph=None):
        # Copied from parent class
        dump = graph is None
        if graph is None:
            graph = rdfio.default_graph()
        rdfgenerator = entity.cw_adapt_to(self.adapter)
        rdfgenerator.fill(graph)
        # Also output related entities
        for rtype, role, adapter in (('in_catalog', 'subject', 'RDFPrimary'),
                                     ('of_dataset', 'object', 'RDFPrimary'),
                                     ('dataset_publisher', 'subject', 'RDFPrimary'),
                                     ('dataset_contact_point', 'subject', 'RDFContactPoint')):
            for related in entity.related(rtype, role, entities=True):
                rdfgenerator = related.cw_adapt_to(adapter)
                rdfgenerator.fill(graph)
        # Copied from parent class
        if dump:
            self._dump(graph)


class DataCatalogDCATRDFView(rdfviews.RDFPrimaryView):
    """RDF view outputting complete information about catalog and children entities.

    This is mainly useful for clients who *do not follow URIs* to gather information about related
    resources and expect all information at one URL (eg. CKAN).
    """

    __regid__ = 'dcat.rdf.complete'
    __select__ = (rdfviews.RDFPrimaryView.__select__ &
                  has_related_entities('in_catalog', role='object'))

    def entity_call(self, entity, graph=None):
        # Copied from parent class
        dump = graph is None
        if graph is None:
            graph = rdfio.default_graph()
        for dataset in entity.related('in_catalog', role='object').entities():
            dataset.view(self.__regid__, graph=graph)
        # Copied from parent class
        if dump:
            self._dump(graph)


class DataCatalogCkanDCATRDFView(rdfviews.RDFPrimaryView):
    """RDF view outputting complete information about catalog and children entities, suitable for
    CKAN.

    This is mainly useful for clients who *do not follow URIs* to gather information about related
    resources and expect all information at one URL (eg. CKAN).
    """

    __regid__ = 'dcat.rdf.ckan'
    __select__ = (rdfviews.RDFPrimaryView.__select__ &
                  has_related_entities('in_catalog', role='object'))
    adapter = 'RDFCkan'

    def entity_call(self, entity, graph=None):
        # Copied from parent class
        dump = graph is None
        if graph is None:
            graph = rdfio.default_graph()
        for dataset in entity.related('in_catalog', role='object').entities():
            dataset.view(self.__regid__, graph=graph)
        # Copied from parent class
        if dump:
            self._dump(graph)


class DatasetCkanDCATRDFView(rdfviews.RDFPrimaryView):
    """RDF view for Dataset entities, suitable for CKAN, outputting complete information about
    catalog, distributions and agents.

    This is mainly useful for clients who *do not follow URIs* to gather information about related
    resources and expect all information at one URL (eg. CKAN).
    """

    __regid__ = 'dcat.rdf.ckan'
    __select__ = rdfviews.RDFPrimaryView.__select__ & is_instance('Dataset')
    adapter = 'RDFCkan'

    def entity_call(self, entity, graph=None):
        # Copied from parent class
        dump = graph is None
        if graph is None:
            graph = rdfio.default_graph()
        rdfgenerator = entity.cw_adapt_to(self.adapter)
        rdfgenerator.fill(graph)
        # Also output related entities
        for rtype, role, adapter in (('in_catalog', 'subject', 'RDFCkan'),
                                     ('of_dataset', 'object', 'RDFCkan'),
                                     ('dataset_publisher', 'subject', 'RDFCkan'),
                                     ('dataset_contact_point', 'subject', 'RDFContactPoint')):
            for related in entity.related(rtype, role, entities=True):
                rdfgenerator = related.cw_adapt_to(adapter)
                rdfgenerator.fill(graph)
        # Copied from parent class
        if dump:
            self._dump(graph)


class RDFExportAction(action.Action):

    __regid__ = 'dcat.rdf-export'
    __select__ = one_line_rset() & is_instance('Dataset', 'DataCatalog')
    title = _('RDF export')

    def url(self):
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        return entity.absolute_url(vid='dcat.rdf.complete')


class CkanRDFExportAction(action.Action):

    __regid__ = 'dcat.rdf.ckan'
    __select__ = one_line_rset() & is_instance('Dataset', 'DataCatalog')
    title = _('RDF export for CKAN')

    def url(self):
        entity = self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0)
        return entity.absolute_url(vid=self.__regid__)


#
# JSON views
#


class CkanJsonLicenseView(jsonviews.JsonMixIn, EntityView):
    """JSON view outputting data about a license that CKAN can use as ``licenses_group_url``. """

    __regid__ = 'dcat.ckan.json.license'
    __select__ = (EntityView.__select__ & score_entity(lambda c: in_license_scheme(c)))

    def entity_call(self, entity, **kwargs):
        # Fetch Open Definition licenses
        od_path = join(dirname(__file__), 'data', 'od_licenses.json')
        with open(od_path) as f:
            od_licenses = json.load(f)
        url2lic = {}
        title2lic = {}
        for lic_dict in od_licenses.values():
            title2lic[lic_dict['title'].lower()] = lic_dict
            if lic_dict['url']:
                urltuple = urlparse.urlsplit(lic_dict['url'])  # Remove {http://,https://} from URL
                url = urltuple.netloc + urltuple.path
                url2lic[url] = lic_dict
        # Build JSON license
        title = entity.label(language_code=u'en')
        url = entity.exact_match[0].uri if entity.exact_match else entity.cwuri
        urltuple = urlparse.urlsplit(url)
        url0 = urltuple.netloc + urltuple.path
        found = url2lic.get(url0, {})  # Find an Open Definition license with same URL
        if not found:
            for title_variant in (  # Find an Open Definition license with same title
                title,
                title.replace('License', 'Licence'),
                re.sub(r'v(\d)', lambda match: match.group(1), title),  # v1.0 -> 1.0
                re.sub(r'v(\d)', lambda match: match.group(1),
                       title.replace('License', 'Licence')),
            ):
                found = title2lic.get(title_variant.lower(), {})
                if found:
                    break
        license = {'title': title, 'url': url}
        for key, default_value in [
            ('domain_content', False),
            ('domain_data', True),
            ('domain_software', False),
            ('family', u''),
            ('id', entity.cwuri),
            ('maintainer', u''),
            ('od_conformance', u'not reviewed'),
            ('osd_conformance', u'not reviewed'),
            ('status', u'active'),
        ]:
            license[key] = found.get(key, default_value)
        self.w(json_dumps(license, sort_keys=True))


class CkanJsonLicensesView(jsonviews.JsonMixIn, EntityView):
    """JSON view outputting data about a license that CKAN can use as ``licenses_group_url``. """

    __regid__ = 'dcat.ckan.json.licenses'
    __select__ = (EntityView.__select__ &
                  score_entity(lambda cs: cs.scheme_relation and
                               cs.scheme_relation[0].name == u'license_type'))

    def entity_call(self, entity, **kwargs):
        licenses = []
        for concept in self._cw.find('Concept', in_scheme=entity).entities():
            licenses.append(json.loads(concept.view('dcat.ckan.json.license')))
        self.w(json_dumps(licenses, sort_keys=True, indent=2))


#
# HTML views
#

class IDownloadableOutOfContextView(baseviews.OutOfContextView):
    """Out of context view for IDownloadable

    Adapted from cubicweb.web.views.idownloadable.IDownloadableOneLineView
    with content-type and a download icon.

    This is used in `file_distribution` relation contextual component in
    particular.
    """

    __select__ = (baseviews.OutOfContextView.__select__ &
                  adaptable('IDownloadable'))
    download_icon = 'glyphicon glyphicon-download-alt'

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        url = xml_escape(entity.absolute_url())
        adapter = entity.cw_adapt_to('IDownloadable')
        name = xml_escape(entity.dc_title())
        durl = xml_escape(adapter.download_url())
        dcontenttype = xml_escape(adapter.download_content_type())
        self.w(u'<a class="{2}" href="{0}" title="{1}"></a> '.format(
               durl, self._cw._('download'), self.download_icon))
        self.w(u'<a href="{0}">{1}</a> '.format(url, name))
        self.w(u'<span class="badge">{0}</span>'.format(dcontenttype))


# File
uicfg.indexview_etype_section['File'] = 'subobject'
pvs.tag_subject_of(('File', 'replaces', '*'), 'hidden')
pvs.tag_object_of(('*', 'replaces', 'File'), 'hidden')
afs.tag_object_of(('*', 'replaces', 'File'), 'main', 'hidden')
abaa.tag_object_of(('*', 'replaces', 'File'), True)

# afs.tag_subject_of(('File', 'resource_of', '*'), 'main', 'hidden')
afs.tag_object_of(('*', 'process_input_file', 'File'), 'main', 'hidden')

pvs.tag_subject_of(('File', 'file_distribution', '*'), 'hidden')


class FileIPrevNextAdapter(navigation.IPrevNextAdapter):
    """IPrevNext adapter for file replaced by or replacing another file.
    """

    __select__ = (has_related_entities('replaces', role='subject') |
                  has_related_entities('replaces', role='object'))

    def next_entity(self):
        successors = self.entity.reverse_replaces
        if successors:
            return successors[0]

    def previous_entity(self):
        predecessors = self.entity.replaces
        if predecessors:
            return predecessors[0]


class FileReplacedBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    """Define <New file version>/<Old file version> breadcrumb."""

    __select__ = (ibreadcrumbs.IBreadCrumbsAdapter.__select__ &
                  has_related_entities('replaces', role='object'))

    def parent_entity(self):
        return self.entity.reverse_replaces[0]


class ScriptImplementationBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    """Define Script / <Implementation> breadcrumbs"""
    __select__ = (ibreadcrumbs.IBreadCrumbsAdapter.__select__ &
                  has_related_entities('implemented_by', role='object') &
                  # Prevent select ambiguity ad File can be object of both
                  # `implemented_by` and `file_distribution` relations.
                  ~has_related_entities('file_distribution', role='subject'))

    def parent_entity(self):
        return self.entity.reverse_implemented_by[0]


class DistributionFileBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    """Define Distribution / File breadcrumbs"""
    __select__ = (ibreadcrumbs.IBreadCrumbsAdapter.__select__ &
                  has_related_entities('file_distribution', role='subject'))

    def parent_entity(self):
        return self.entity.file_distribution[0]


# Agent
abaa.tag_object_of(('*', 'catalog_publisher', 'Agent'), True)
afs.tag_object_of(('*', 'catalog_publisher', 'Agent'), 'main', 'hidden')
affk.set_field_kwargs('Agent', 'name', widget=fw.TextInput({'size': 82}))
affk.set_field_kwargs('Agent', 'email', widget=fw.TextInput({'size': 82}))
pvs.tag_subject_of(('Agent', 'publisher_type', 'Concept'), 'attributes')
afs.tag_subject_of(('Agent', 'publisher_type', 'Concept'), 'main', 'attributes')


# Concept

def license_scheme_relation_choices(form, field, **kwargs):
    """Choices function for CheckBox widget to select/unselect whether a scheme
    is used to qualify a license_type relationship.
    """
    rtype_eid = form._cw.find('CWRType', name=u'license_type')[0][0]
    return [(u'', unicode(rtype_eid))]


def in_license_scheme(entity):
    """Return 1 if entity is a Concept in a scheme used to describe license
    type.
    """
    if not entity.cw_etype == 'Concept':
        return 0
    if not entity.has_eid():
        return 0
    scheme = entity.in_scheme[0]
    if (scheme.scheme_relation and
            scheme.scheme_relation[0].name == u'license_type'):
        return 1
    return 0


pvs.tag_subject_of(('Concept', 'license_type', 'Concept'), 'hidden')

license_concept_pvs = build_selectable_uicfg(pvs, score_entity(in_license_scheme))
license_concept_pvs.tag_subject_of(('Concept', 'license_type', 'Concept'), 'attributes')


afs.tag_subject_of(('Concept', 'license_type', 'Concept'), 'main', 'hidden')
afs.tag_object_of(('Concept', 'license_type', 'Concept'), 'main', 'hidden')
for rtype in ('publisher_type', 'language', 'dataset_frequency', 'dcat_theme',
              'license', 'distribution_media_type', 'distribution_format'):
    afs.tag_object_of(('*', rtype, 'Concept'), 'main', 'hidden')
afs.tag_subject_of(('Concept', 'license', '*'), 'main', 'hidden')

licence_concept_afs = build_selectable_uicfg(afs, score_entity(in_license_scheme))
licence_concept_afs.tag_subject_of(('Concept', 'license_type', 'Concept'), 'main', 'attributes')
afs.tag_object_of(('*', 'theme_taxonomy', 'ConceptScheme'), 'main', 'hidden')
afs.tag_subject_of(('ConceptScheme', 'scheme_relation', '*'), 'main', 'attributes')
affk.tag_subject_of(('ConceptScheme', 'scheme_relation', '*'),
                    {'label': _('describes licenses?'), 'help': u'',
                     'widget': fw.CheckBox, 'choices': license_scheme_relation_choices})


# DataCatalog
pvs.tag_attribute(('DataCatalog', 'title'), 'hidden')
pvs.tag_attribute(('DataCatalog', 'issued'), 'hidden')
afs.tag_attribute(('DataCatalog', 'issued'), 'main', 'hidden')
pvs.tag_attribute(('DataCatalog', 'modified'), 'hidden')
afs.tag_attribute(('DataCatalog', 'modified'), 'main', 'hidden')
pvs.tag_subject_of(('DataCatalog', 'catalog_publisher', '*'), 'hidden')
pvs.tag_subject_of(('DataCatalog', 'license', '*'), 'attributes')
afs.tag_subject_of(('DataCatalog', 'theme_taxonomy', '*'), 'main', 'attributes')
afs.tag_subject_of(('DataCatalog', 'catalog_publisher', '*'), 'main', 'attributes')
abaa.tag_object_of(('*', 'in_catalog', 'DataCatalog'), True)
abaa.tag_subject_of(('DataCatalog', 'theme_taxonomy', '*'), True)
afs.tag_object_of(('*', 'in_catalog', 'DataCatalog'), 'main', 'hidden')
pvdc.tag_attribute(('DataCatalog', 'homepage'), {'vid': 'urlattr'})
for attr in ('title', 'homepage'):
    affk.set_field_kwargs('DataCatalog', attr, widget=fw.TextInput({'size': 82}))
afs.tag_subject_of(('DataCatalog', 'license', 'Concept'), 'main', 'attributes')


class DataCatalogBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    """Define <Agent>/<DataCatalog> breadcrumb."""

    __select__ = (ibreadcrumbs.IBreadCrumbsAdapter.__select__ &
                  has_related_entities('catalog_publisher'))

    def parent_entity(self):
        return self.entity.catalog_publisher[0]


# Dataset

def dataset_publisher_choices(form, field, **kwargs):
    """Return form field choices corresponding to all possible publishers for a dataset."""
    # Try to find out if this dataset is linked to a catalog
    linkedto = form.linked_to.get(('in_catalog', 'subject'))
    if linkedto:  # Adding dataset from a catalog view
        catalog = form._cw.entity_from_eid(linkedto[0])
        publishers = catalog.catalog_publisher
        publisher = publishers[0] if publishers else None
        if publisher is not None:
            return [(publisher.dc_title(), unicode(publisher.eid))]
    limit = kwargs.get('limit', 50)
    qs = 'DISTINCT Agent X LIMIT {limit}'.format(limit=limit)
    return [(entity.dc_title(), unicode(entity.eid)) for entity in form._cw.execute(qs).entities()]

pvs.tag_subject_of(('Dataset', 'in_catalog', '*'), 'hidden')
pvs.tag_subject_of(('Dataset', 'dataset_frequency', '*'), 'attributes')
pvs.tag_subject_of(('Dataset', 'dataset_contact_point', '*'), 'attributes')
pvs.tag_subject_of(('Dataset', 'dataset_publisher', '*'), 'attributes')
pvdc.tag_attribute(('Dataset', 'landing_page'), {'vid': 'urlattr'})
afs.tag_subject_of(('Dataset', 'dataset_contact_point', '*'), 'main', 'attributes')
afs.tag_subject_of(('Dataset', 'dataset_publisher', '*'), 'main', 'attributes')
pvs.tag_subject_of(('Dataset', 'dataset_contributors', '*'), 'attributes')
afs.tag_subject_of(('Dataset', 'dataset_contributors', '*'), 'main', 'attributes')
pvs.tag_attribute(('Dataset', 'title'), 'hidden')
pvs.tag_attribute(('Dataset', 'identifier'), 'hidden')
afs.tag_attribute(('Dataset', 'identifier'), 'main', 'hidden')
pvs.tag_attribute(('Dataset', 'issued'), 'hidden')
afs.tag_attribute(('Dataset', 'issued'), 'main', 'hidden')
pvs.tag_attribute(('Dataset', 'modified'), 'hidden')
afs.tag_attribute(('Dataset', 'modified'), 'main', 'hidden')
# Keep dcat_theme hidden from autoform since the RelationWidget will not work
# on creation as constraints on DataCatalog cannot be checked and we prefer
# the user to edit this *inline* from the primary view.
afs.tag_subject_of(('Dataset', 'dcat_theme', '*'), 'main', 'hidden')
pvs.tag_subject_of(('Dataset', 'dcat_theme', '*'), 'attributes')
affk.tag_subject_of(('Dataset', 'dcat_theme', '*'),
                    {'widget': rwdg.RelationFacetWidget(no_creation_form=True)})
afs.tag_subject_of(('Dataset', 'in_catalog', '*'), 'main', 'attributes')
afs.tag_object_of(('*', 'resource_feed_of', 'Dataset'), 'main', 'hidden')
afs.tag_object_of(('*', 'of_dataset', 'Dataset'), 'main', 'hidden')
for attr in ('identifier', 'title', 'keyword', 'landing_page',
             'provenance'):
    affk.set_field_kwargs('Dataset', attr, widget=fw.TextInput({'size': 82}))
afs.tag_subject_of(('Dataset', 'dataset_frequency', 'Concept'),
                   'main', 'attributes')
affk.tag_subject_of(('Dataset', 'dataset_publisher', '*'),
                    {'choices': dataset_publisher_choices})


class DatasetPublisherFacet(cwfacet.RelationFacet):
    __regid__ = 'datacat.dataset_publisher_facet'
    __select__ = cwfacet.RelationFacet.__select__ & is_instance('Dataset')
    rtype = 'dataset_publisher'
    role = 'subject'
    target_attr = 'name'


class DatasetInCatalogFacet(cwfacet.RelationFacet):
    __regid__ = 'datacat.dataset_in_catalog_facet'
    __select__ = cwfacet.RelationFacet.__select__ & is_instance('Dataset')
    rtype = 'in_catalog'
    role = 'subject'
    target_attr = 'title'


class DatasetIssuedFacet(cwfacet.DateRangeFacet):
    """Facet filtering datasets based on their publication date."""
    __regid__ = 'datacat.dataset_issued_facet'
    __select__ = cwfacet.DateRangeFacet.__select__ & is_instance('Dataset')
    rtype = 'issued'


class DatasetModifiedFacet(cwfacet.DateRangeFacet):
    """Facet filtering datasets based on their modification date."""
    __regid__ = 'datacat.dataset_modified_facet'
    __select__ = cwfacet.DateRangeFacet.__select__ & is_instance('Dataset')
    rtype = 'modified'


class DatasetCatalogBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    """Define DataCatalog / Dataset breadcrumbs"""
    __select__ = (ibreadcrumbs.IBreadCrumbsAdapter.__select__ &
                  has_related_entities('in_catalog', role='subject'))

    def parent_entity(self):
        return self.entity.in_catalog[0]


class DatasetHasDistributionFacet(cwfacet.HasRelationFacet):
    """Facet filtering datasets with a distribution."""
    __regid__ = 'datacat.has_distribution'
    __select__ = cwfacet.HasRelationFacet.__select__ & is_instance('Dataset')
    rtype, role = 'of_dataset', 'object'


# Distribution

class DistributionBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    """Define Dataset / Distribution breadcrumbs"""
    __select__ = (ibreadcrumbs.IBreadCrumbsAdapter.__select__ &
                  has_related_entities('of_dataset', role='subject'))

    def parent_entity(self):
        return self.entity.of_dataset[0]


pvs.tag_attribute(('Distribution', 'title'), 'hidden')
affk.set_field_kwargs('Distribution', 'title', widget=fw.TextInput({'size': 82}))
afs.tag_object_of(('*', 'file_distribution', 'Distribution'), 'main', 'inlined')
abaa.tag_object_of(('*', 'file_distribution', 'Distribution'), True)
afs.tag_attribute(('Distribution', 'byte_size'), 'main', 'hidden')
afs.tag_attribute(('Distribution', 'download_url'), 'main', 'hidden')
afs.tag_attribute(('Distribution', 'issued'), 'main', 'hidden')
afs.tag_attribute(('Distribution', 'modified'), 'main', 'hidden')
pvs.tag_subject_of(('Distribution', 'license', '*'), 'attributes')
pvs.tag_subject_of(('Distribution', 'distribution_media_type', '*'), 'attributes')
pvs.tag_subject_of(('Distribution', 'distribution_format', '*'), 'attributes')
afs.tag_subject_of(('Distribution', 'license', '*'), 'main', 'inlined')
affk.tag_subject_of(
    ('Distribution', 'distribution_format', 'Concept'),
    {'widget': _autocomplete_widget('get_filetypes')},
)
affk.tag_subject_of(
    ('Distribution', 'distribution_media_type', 'Concept'),
    {'widget': _autocomplete_widget('get_mediattypes')},
)
afs.tag_subject_of(('Distribution', 'license', 'Concept'), 'main', 'attributes')


@ajaxcontroller.ajaxfunc(output_type='json')
def get_filetypes(self):
    return search_in_scheme(
        self._cw, 'http://publications.europa.eu/resource/authority/file-type')


@ajaxcontroller.ajaxfunc(output_type='json')
def get_mediattypes(self):
    return search_in_scheme(
        self._cw, 'http://www.iana.org/assignments/media-types/media-types.xml')


pvs.tag_attribute(('Distribution', 'access_url'), 'hidden')
afs.tag_attribute(('Distribution', 'access_url'), 'main', 'hidden')
pvs.tag_attribute(('Distribution', 'download_url'), 'hidden')
afs.tag_attribute(('Distribution', 'download_url'), 'main', 'hidden')
pvs.tag_subject_of(('Distribution', 'of_dataset', '*'), 'hidden')
afs.tag_subject_of(('Distribution', 'of_dataset', '*'), 'main', 'hidden')
pvs.tag_subject_of(('Distribution', 'distribution_format', '*'), 'attributes')
afs.tag_subject_of(('Distribution', 'distribution_format', '*'), 'main', 'attributes')
pvs.tag_subject_of(('Distribution', 'distribution_media_type', '*'), 'attributes')
afs.tag_subject_of(('Distribution', 'distribution_media_type', '*'), 'main', 'attributes')
pvs.tag_attribute(('Distribution', 'issued'), 'hidden')
afs.tag_attribute(('Distribution', 'issued'), 'main', 'hidden')
pvs.tag_attribute(('Distribution', 'modified'), 'hidden')
afs.tag_attribute(('Distribution', 'modified'), 'main', 'hidden')
pvs.tag_attribute(('Distribution', 'byte_size'), 'hidden')
afs.tag_attribute(('Distribution', 'byte_size'), 'main', 'hidden')


# XXX does not work except in creation mode.
distr_afs = build_selectable_uicfg(afs, has_related_entities('file_distribution'))
distr_afs.tag_attribute(('File', 'title'), 'main', 'hidden')
distr_afs.tag_attribute(('File', 'description'), 'main', 'hidden')


# ResourceFeed
pvdc.tag_attribute(('ResourceFeed', 'url'), {'vid': 'urlattr'})
pvs.tag_attribute(('ResourceFeed', 'title'), 'hidden')
pvs.tag_subject_of(('ResourceFeed', 'resource_feed_of', '*'), 'hidden')
afs.tag_subject_of(('ResourceFeed', 'resource_feed_of', '*'), 'main', 'hidden')
pvs.tag_object_of(('*', 'process_for_resourcefeed', 'ResourceFeed'), 'hidden')
afs.tag_subject_of(('ResourceFeed', 'resource_feed_source', '*'),
                   'main', 'hidden')
for rtype in ('transformation_script', 'validation_script'):
    afs.tag_subject_of(('ResourceFeed', rtype, '*'),
                       'main', 'attributes')
    abaa.tag_subject_of(('ResourceFeed', rtype, '*'), True)
abaa.tag_object_of(('*', 'process_for_resourcefeed', 'ResourceFeed'), False)


class ResourceFeedBreadCrumbsAdapter(ibreadcrumbs.IBreadCrumbsAdapter):
    """Define Dataset / ResourceFeed breadcrumbs"""
    __select__ = (ibreadcrumbs.IBreadCrumbsAdapter.__select__ &
                  has_related_entities('resource_feed_of', role='subject'))

    def parent_entity(self):
        """The Dataset"""
        return self.entity.resource_feed_of[0]


class DataProcessInResourceFeedCtxComponent(component.EntityCtxComponent):
    """Display data processes in ResourceFeed primary view"""
    __regid__ = 'datacat.resourcefeed-dataprocess'
    __select__ = (component.EntityCtxComponent.__select__ &
                  is_instance('ResourceFeed') &
                  has_related_entities('process_for_resourcefeed',
                                       role='object'))
    title = _('Data processes')
    context = 'navcontentbottom'

    def render_body(self, w):
        rset = self._cw.execute(
            'Any P,I,S,D WHERE P process_for_resourcefeed X,'
            '                  P process_input_file I,'
            '                  P in_state ST, ST name S,'
            '                  D? process_depends_on P,'
            '                  X eid %(eid)s',
            {'eid': self.entity.eid})
        if rset:
            w(self._cw.view('table', rset=rset))
        rset = self._cw.execute(
            'Any P,I,S,D WHERE P process_for_resourcefeed X,'
            '                  P process_input_file I,'
            '                  P in_state ST, ST name S,'
            '                  P process_depends_on D?,'
            '                  X eid %(eid)s',
            {'eid': self.entity.eid})
        if rset:
            w(self._cw.view('table', rset=rset))


# Script
afs.tag_object_of(('*', 'process_script', 'Script'),
                  'main', 'hidden')
afs.tag_subject_of(('Script', 'implemented_by', '*'), 'main', 'inlined')
pvs.tag_attribute(('Script', 'name'), 'hidden')


# DataTransformationProcess, DataValidationProcess
for etype in ('DataTransformationProcess', 'DataValidationProcess'):
    uicfg.indexview_etype_section[etype] = 'subobject'
    afs.tag_subject_of((etype, 'process_input_file', '*'),
                       'main', 'attributes')
    pvs.tag_subject_of((etype, 'process_input_file', '*'), 'attributes')
    affk.set_fields_order(etype, ('name', 'description',
                                  ('process_input_file', 'subject')))
