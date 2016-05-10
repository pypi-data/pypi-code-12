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

"""cubicweb-datacat tests for views"""

from datetime import datetime
import json
from tempfile import NamedTemporaryFile

from mock import patch
from pytz import utc
from rdflib.compare import to_isomorphic, graph_diff

from cubicweb.devtools.testlib import CubicWebTC

from cubes.skos.rdfio import default_graph
from cubes.datacat.views import dataset_publisher_choices

from utils import mock_entity_cw_url, mock_concept_cwuri


class PublisherChoicesFunctionTC(CubicWebTC):
    """Test case for cubicweb-datacat dataset publisher choices function."""

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            pub1 = cnx.create_entity('Agent', name=u'Publisher 1')
            pub2 = cnx.create_entity('Agent', name=u'Publisher 2')
            cat = cnx.create_entity('DataCatalog', title=u'My Catalog',
                                    description=u'A nice catalog', catalog_publisher=pub1)
            cnx.commit()
        self.cat_eid = cat.eid
        self.pub1_eid = pub1.eid
        self.pub2_eid = pub2.eid

    def test_choices_add_dataset_from_catalog(self):
        """Check that publisher list is correct when dataset is created from a catalog."""
        with self.admin_access.web_request() as req:
            req.form['__linkto'] = 'in_catalog:{0}:subject'.format(self.cat_eid)
            dset_class = self.vreg['etypes'].etype_class('Dataset')(req)
            add_form = self.vreg['forms'].select('edition', req, entity=dset_class)
            publisher_field = add_form.field_by_name('dataset_publisher', 'subject')
            self.assertEqual(dataset_publisher_choices(add_form, publisher_field),
                             [(u'Publisher 1', unicode(self.pub1_eid))])

    def test_choices_add_dataset_no_catalog(self):
        """Check that publisher list is correct when dataset is created standalone."""
        with self.admin_access.web_request() as req:
            dset_class = self.vreg['etypes'].etype_class('Dataset')(req)
            add_form = self.vreg['forms'].select('edition', req, entity=dset_class)
            publisher_field = add_form.field_by_name('dataset_publisher', 'subject')
            self.assertEqual(dataset_publisher_choices(add_form, publisher_field),
                             [(u'Publisher 1', unicode(self.pub1_eid)),
                              (u'Publisher 2', unicode(self.pub2_eid))])


def sorted_triples(graph):
    return sorted(graph.serialize(format='nt').splitlines())


class RDFAdapterTC(CubicWebTC):
    """Test case for RDF data export."""

    def setup_database(self):
        # patch now() so that computed datetime attributes always return the same datetime
        # See https://docs.python.org/3/library/unittest.mock-examples.html#partial-mocking
        with patch('cubes.datacat.hooks.datetime') as mock_dt:
            mock_dt.now.return_value = datetime(2016, 02, 02, 15, 25, 0, tzinfo=utc)
            mock_dt.side_effect = datetime
            # Now set up entities
            with self.admin_access.repo_cnx() as cnx:
                lic_scheme = cnx.create_entity('ConceptScheme',
                                               cwuri=u'http://publications.europa.eu/'
                                               'resource/authority/licence')
                cnx.execute('SET CS scheme_relation RT WHERE CS eid %(cs)s, RT name %(rt)s',
                            {'cs': lic_scheme.eid, 'rt': 'license_type'})
                scheme = cnx.create_entity('ConceptScheme', cwuri=u'http://example.org/scheme',
                                           title=u'Concept Scheme')
                nat_concept = scheme.add_concept(u'National authority')
                attribution_concept = scheme.add_concept(u'Attribution')
                annual_concept = scheme.add_concept(u'Annual')
                csv_concept = scheme.add_concept(u'CSV')
                xls_concept = scheme.add_concept(u'Excel XLS')
                appxls_concept = scheme.add_concept(u'application/vnd.ms-excel')
                zip_concept = scheme.add_concept(u'ZIP')
                appzip_concept = scheme.add_concept(u'application/zip')
                eng_concept = scheme.add_concept(u'English')
                edu_concept = scheme.add_concept(u'Education, culture and sport')
                publisher = cnx.create_entity('Agent', name=u'The Publisher',
                                              publisher_type=nat_concept,
                                              email=u'publisher@example.org')
                contact = cnx.create_entity('Agent', name=u'The Contact Point',
                                            email=u'contact@example.org')
                license = cnx.create_entity('Concept', in_scheme=lic_scheme,
                                            license_type=attribution_concept)
                cnx.create_entity('Label', label_of=license, kind=u"preferred",
                                  label=u'Other (attribution)')
                cat = cnx.create_entity('DataCatalog', title=u'My Catalog',
                                        description=u'A nice catalog', catalog_publisher=publisher,
                                        homepage=u'http://cat.example.org', language=eng_concept,
                                        theme_taxonomy=scheme, license=license,
                                        issued=datetime(2016, 02, 01, 20, 40, 0, tzinfo=utc),
                                        modified=datetime(2016, 02, 02, 18, 25, 0, tzinfo=utc))
                ds = cnx.create_entity('Dataset', title=u'First Dataset', description=u'A dataset',
                                       in_catalog=cat, dataset_publisher=publisher,
                                       dataset_contact_point=contact, keyword=u'keyword',
                                       dataset_frequency=annual_concept, dcat_theme=edu_concept)
                csv_dist = cnx.create_entity('Distribution', title=u'First Dataset (CSV)',
                                             description=u'First Dataset in CSV format',
                                             of_dataset=ds, license=license,
                                             distribution_format=csv_concept,
                                             access_url=u'http://www.example.org')
                xls_dist = cnx.create_entity('Distribution', title=u'First Dataset (XLS)',
                                             description=u'First Dataset in XLS format',
                                             of_dataset=ds, license=license,
                                             distribution_format=xls_concept,
                                             distribution_media_type=appxls_concept,
                                             access_url=u'http://www.example.org')
                zip_dist = cnx.create_entity('Distribution', title=u'First Dataset (ZIP)',
                                             description=u'First Dataset in ZIP format',
                                             of_dataset=ds, license=license,
                                             distribution_format=zip_concept,
                                             distribution_media_type=appzip_concept,
                                             access_url=u'http://www.example.org')
                cnx.commit()
                self.entities_to_mock = [
                    (scheme.eid, 'http://example.org/concept_scheme'),
                    (publisher.eid, 'http://example.org/publisher'),
                    (contact.eid, 'http://example.org/contact'),
                    (cat.eid, u'http://example.org/catalog'),
                    (ds.eid, 'http://example.org/dataset'),
                    (csv_dist.eid, 'http://example.org/dataset/csv'),
                    (xls_dist.eid, 'http://example.org/dataset/xls'),
                    (zip_dist.eid, 'http://example.org/dataset/zip'),
                ]
                self.concepts_to_mock = [
                    (nat_concept.eid, u'http://example.org/national_authority'),
                    (attribution_concept.eid, u'http://example.org/attribution'),
                    (annual_concept.eid, u'http://example.org/annual'),
                    (csv_concept.eid, u'http://example.org/csv'),
                    (xls_concept.eid, u'http://example.org/xls'),
                    (zip_concept.eid, u'http://example.org/zip'),
                    (appxls_concept.eid, u'http://example.org/application_xls'),
                    (appzip_concept.eid, u'http://example.org/application_zip'),
                    (eng_concept.eid, u'http://example.org/english'),
                    (edu_concept.eid, u'http://example.org/education'),
                    (license.eid, 'http://example.org/license'),
                ]
                self.cat_eid = cat.eid

    @patch('cubes.skos.rdfio.RDFGraphGenerator.same_as_uris')
    def _check_rdf_view(self, action_regid, expected_fname, mock_same_as_uris):
        # Because we mock either cwuri or absolute_url, RDFGraphGenerator will add `sameAS` triples
        # on exported entities. We don't want this
        mock_same_as_uris.return_value = []
        with self.admin_access.client_cnx() as cnx:
            # Mock entities to have predictable URIs (no eid)
            for eid, fake_url in self.entities_to_mock:
                mock_entity_cw_url(cnx, eid, fake_url)
            for eid, fake_url in self.concepts_to_mock:
                mock_concept_cwuri(cnx, eid, fake_url)
            # Now call export
            cat = cnx.entity_from_eid(self.cat_eid)
            with NamedTemporaryFile() as f:
                f.write(cat.view(action_regid))
                f.seek(0)
                graph = default_graph()
                graph.load('file://' + f.name, rdf_format='xml')
            expected_graph = default_graph()
            expected_graph.load('file://' + self.datapath(expected_fname), rdf_format='xml')
            iso1 = to_isomorphic(graph._graph)
            iso2 = to_isomorphic(expected_graph._graph)
            in_both, in_first, in_second = graph_diff(iso1, iso2)
            self.assertEqual(iso1, iso2, u'RDF graphs are not the same:\n'
                             '* Only in actual:\n{0}\n\n'
                             '* Only in expected:\n{1}'.format(
                                 sorted_triples(in_first), sorted_triples(in_second)))

    def test_complete_rdf_view(self):
        """Check that 'RDF export' action produce valid DCAT RDF data."""
        self._check_rdf_view('dcat.rdf.complete', 'valid_export.xml')

    def test_ckan_rdf_view(self):
        """Check that 'RDF export for CKAN' action produce RDF data suitable for CKAN."""
        self._check_rdf_view('dcat.rdf.ckan', 'ckan_export.rdf')


class CkanJsonLicenseExportTC(CubicWebTC):
    """Test case for JSON license export to be used with CKAN."""

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            lic_scheme = cnx.create_entity('ConceptScheme',
                                           cwuri=u'http://publications.europa.eu/'
                                           'resource/authority/licence')
            cnx.execute('SET CS scheme_relation RT WHERE CS eid %(cs)s, RT name %(rt)s',
                        {'cs': lic_scheme.eid, 'rt': 'license_type'})
            # Licence with match in OpenDefinition by URL
            cc_by_40 = cnx.create_entity('Concept', in_scheme=lic_scheme,
                                         cwuri=u'http://creativecommons.org/licenses/by/4.0/')
            cnx.create_entity('Label', label_of=cc_by_40,
                              label=u'Creative Commons Attribution 4.0 International',
                              kind=u"preferred", language_code=u'en')
            # Licence with match in OpenDefinition by title
            pddl = cnx.create_entity('Concept', in_scheme=lic_scheme,
                                     cwuri=u'http://opendatacommons.org/licenses/pddl/1.0/')
            cnx.create_entity('Label', label_of=pddl,
                              label=u'Open Data Commons Public Domain Dedication and License v1.0',
                              kind=u"preferred", language_code=u'en')
            # Licence with no match in OpenDefinition
            other_at = cnx.create_entity('Concept', in_scheme=lic_scheme,
                                         cwuri=u'http://example.org/lo-ol')
            cnx.create_entity('Label', label_of=other_at, label=u'Licence Ouverte / Open Licence',
                              kind=u"preferred", language_code=u'en')
            cnx.commit()
            self.lic_scheme_eid = lic_scheme.eid

    def test_ckan_json_license_scheme_export(self):
        """Check that a license concept scheme is exported correctly for CKAN."""
        with self.admin_access.web_request() as req:
            lic_scheme = req.execute('ConceptScheme CS WHERE CS scheme_relation RT, '
                                     'RT name "license_type"').one()
            export = json.loads(lic_scheme.view('dcat.ckan.json.licenses'))
            with open(self.datapath('licenses.json')) as f:
                expected = json.load(f)
            self.assertEqual(export, expected)


if __name__ == '__main__':
    import unittest
    unittest.main()
