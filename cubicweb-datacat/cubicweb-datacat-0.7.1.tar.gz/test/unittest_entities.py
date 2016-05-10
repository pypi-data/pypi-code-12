"""cubicweb-datacat unit tests for entities"""

import datetime

from cubicweb.devtools.testlib import CubicWebTC

from cubes.skos import rdfio

from utils import create_file


class IDataProcessTC(CubicWebTC):

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            cat = cnx.create_entity('DataCatalog', title=u'My Catalog', description=u'A catalog',
                                    catalog_publisher=cnx.create_entity('Agent', name=u'Publisher'))
            ds = cnx.create_entity('Dataset', title=u'Test dataset', description=u'A dataset',
                                   in_catalog=cat)
            s = cnx.create_entity('Script', name=u's')
            create_file(cnx, 'pass', reverse_implemented_by=s)
            cnx.commit()
            self.dataset_eid = ds.eid
            self.script_eid = s.eid

    def _create_process(self, cnx, etype, **kwargs):
        with cnx.security_enabled(write=False):
            kwargs.setdefault('process_script', self.script_eid)
            process = cnx.create_entity(etype, **kwargs)
            cnx.commit()
            return process

    def test_process_type(self):
        with self.admin_access.repo_cnx() as cnx:
            for etype, ptype in [('DataTransformationProcess', 'transformation'),
                                 ('DataValidationProcess', 'validation')]:
                p = self._create_process(cnx, etype)
                cnx.commit()
                self.assertEqual(p.cw_adapt_to('IDataProcess').process_type,
                                 ptype)

    def test_state_name(self):
        with self.admin_access.repo_cnx() as cnx:
            p = self._create_process(cnx, 'DataValidationProcess')
            cnx.commit()
            idataprocess = p.cw_adapt_to('IDataProcess')
            self.assertEqual(idataprocess.state_name('error'),
                             'wfs_dataprocess_error')
            with self.assertRaises(ValueError) as cm:
                idataprocess.state_name(u'blah')
            self.assertIn('invalid state name', str(cm.exception))

    def test_tr_name(self):
        with self.admin_access.repo_cnx() as cnx:
            p = self._create_process(cnx, 'DataTransformationProcess')
            cnx.commit()
            idataprocess = p.cw_adapt_to('IDataProcess')
            self.assertEqual(idataprocess.tr_name('start'),
                             'wft_dataprocess_start')
            with self.assertRaises(ValueError) as cm:
                idataprocess.tr_name(u'blah')
            self.assertIn('invalid transition name', str(cm.exception))


class RDFAdapterTC(CubicWebTC):
    """Test case for RDF data export."""

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            lic_scheme = cnx.create_entity('ConceptScheme', cwuri=u'http://publications.europa.eu/'
                                           'resource/authority/licence')
            cnx.execute('SET CS scheme_relation RT WHERE CS eid %(cs)s, RT name %(rt)s',
                        {'cs': lic_scheme.eid, 'rt': 'license_type'})
            scheme = cnx.create_entity('ConceptScheme', cwuri=u'http://example.org/scheme')
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
                                        cwuri=u'http://creativecommons.org/licenses/by/3.0',
                                        license_type=attribution_concept)
            cnx.create_entity('Label', label_of=license, kind=u"preferred",
                              label=u'Creative Commons Attribution')
            cat = cnx.create_entity('DataCatalog', title=u'My Catalog',
                                    description=u'A nice catalog', catalog_publisher=publisher,
                                    homepage=u'http://cat.example.org', language=eng_concept,
                                    theme_taxonomy=scheme, license=license,
                                    issued=datetime.datetime(2016, 02, 01, 20, 40, 00),
                                    modified=datetime.datetime(2016, 02, 02, 18, 25, 00))
            ds = cnx.create_entity('Dataset', title=u'First Dataset', description=u'A nice datacat',
                                   in_catalog=cat, dataset_publisher=publisher,
                                   dataset_contact_point=contact, keyword=u'keyword',
                                   dataset_frequency=annual_concept, dcat_theme=edu_concept)
            dist1 = cnx.create_entity('Distribution', title=u'First Dataset (CSV)',
                                      description=u'First Dataset in CSV format', of_dataset=ds,
                                      license=license, distribution_format=csv_concept,
                                      access_url=u'http://www.example.org')
            dist2 = cnx.create_entity('Distribution', title=u'First Dataset (XLS)',
                                      description=u'First Dataset in XLS format', of_dataset=ds,
                                      license=license, distribution_format=xls_concept,
                                      distribution_media_type=appxls_concept,
                                      access_url=u'http://www.example.org')
            dist3 = cnx.create_entity('Distribution', title=u'First Dataset (ZIP)',
                                      description=u'First Dataset in ZIP format', of_dataset=ds,
                                      license=license, distribution_format=zip_concept,
                                      distribution_media_type=appzip_concept,
                                      access_url=u'http://www.example.org')
            cnx.commit()
            self.cat_eid = cat.eid
            self.ds_eid = ds.eid
            self.dist1_eid = dist1.eid
            self.dist2_eid = dist2.eid
            self.dist3_eid = dist3.eid
            self.publisher_eid = publisher.eid
            self.contact_eid = contact.eid
            self.license_eid = license.eid
            self.nat_concept_uri = nat_concept.cwuri
            self.attribution_concept_uri = attribution_concept.cwuri
            self.annual_concept_uri = annual_concept.cwuri
            self.csv_concept_uri = csv_concept.cwuri
            self.xls_concept_uri = xls_concept.cwuri
            self.appxls_concept_uri = appxls_concept.cwuri
            self.zip_concept_uri = zip_concept.cwuri
            self.appzip_concept_uri = appzip_concept.cwuri
            self.eng_concept_uri = eng_concept.cwuri
            self.theme_scheme_uri = scheme.cwuri
            self.edu_concept_uri = edu_concept.cwuri

    def test_rdf_export_catalog(self):
        """Check that we get expected RDF data when exporting a catalog."""
        with self.admin_access.repo_cnx() as cnx:
            cat = cnx.entity_from_eid(self.cat_eid)
            publisher = cnx.entity_from_eid(self.publisher_eid)
            cat_uri = cat.absolute_url()
            rdfcat = cat.cw_adapt_to('RDFPrimary')
            graph = rdfio.default_graph()
            rdfcat.fill(graph)
            self._check_literal_property(graph,
                                         cat_uri, 'http://purl.org/dc/terms/title', u'My Catalog')
            self._check_uri_property(graph, cat_uri, 'http://purl.org/dc/terms/publisher',
                                     publisher.absolute_url())
            self._check_uri_property(graph, cat_uri, 'http://xmlns.com/foaf/0.1/homepage',
                                     'http://cat.example.org')
            self._check_uri_property(graph, cat_uri, 'http://purl.org/dc/terms/language',
                                     self.eng_concept_uri)
            self._check_uri_property(graph, cat_uri, 'http://www.w3.org/ns/dcat#themeTaxonomy',
                                     self.theme_scheme_uri)
            self._check_literal_property(graph, publisher.absolute_url(),
                                         'http://xmlns.com/foaf/0.1/name',
                                         u'The Publisher')

    def test_rdf_export_dataset(self):
        """Check that we get expected RDF data when exporting a catalog."""
        with self.admin_access.repo_cnx() as cnx:
            ds = cnx.entity_from_eid(self.ds_eid)
            publisher = cnx.entity_from_eid(self.publisher_eid)
            contact = cnx.entity_from_eid(self.contact_eid)
            ds_uri = ds.absolute_url()
            rdfds = ds.cw_adapt_to('RDFPrimary')
            graph = rdfio.default_graph()
            rdfds.fill(graph)
            self._check_literal_property(graph,
                                         ds_uri, 'http://purl.org/dc/terms/title', u'First Dataset')
            self._check_literal_property(graph,
                                         ds_uri, 'http://www.w3.org/ns/dcat#keyword',
                                         u'keyword')
            self._check_uri_property(graph, ds_uri, 'http://purl.org/dc/terms/publisher',
                                     publisher.absolute_url())
            self._check_uri_property(graph, ds_uri, 'http://www.w3.org/ns/dcat#contactPoint',
                                     contact.absolute_url())
            self._check_uri_property(graph, ds_uri, 'http://purl.org/dc/terms/accrualPeriodicity',
                                     self.annual_concept_uri)
            self._check_uri_property(graph, ds_uri, 'http://www.w3.org/ns/dcat#theme',
                                     self.edu_concept_uri)

    def test_rdf_export_distribution(self):
        """Check that we get expected RDF data when exporting a distribution."""
        with self.admin_access.repo_cnx() as cnx:
            for dist_eid, title, filetype, mediatype in [
                (self.dist1_eid, u'First Dataset (CSV)', self.csv_concept_uri, None),
                (self.dist2_eid, u'First Dataset (XLS)', self.xls_concept_uri,
                 self.appxls_concept_uri),
                (self.dist3_eid, u'First Dataset (ZIP)', self.zip_concept_uri,
                 self.appzip_concept_uri),
            ]:
                dist = cnx.entity_from_eid(dist_eid)
                license = cnx.entity_from_eid(self.license_eid)
                dist_uri = dist.absolute_url()
                rdfdist = dist.cw_adapt_to('RDFPrimary')
                graph = rdfio.default_graph()
                rdfdist.fill(graph)
                self._check_literal_property(graph, dist_uri, 'http://purl.org/dc/terms/title',
                                             title)
                if title == u'First Dataset (CSV)':
                    self._check_uri_property(graph, dist_uri, 'http://purl.org/dc/terms/license',
                                             license.cwuri)
                    self._check_uri_property(graph, license.cwuri,
                                             'http://purl.org/dc/terms/type',
                                             self.attribution_concept_uri)
                    self._check_uri_property(graph, license.cwuri,
                                             'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
                                             'http://purl.org/dc/terms/LicenseDocument')
                    self._check_literal_property(graph, license.cwuri,
                                                 'http://purl.org/dc/terms/title',
                                                 u'Creative Commons Attribution')
                if filetype is not None:
                    self._check_uri_property(graph, dist_uri, 'http://purl.org/dc/terms/format',
                                             filetype)
                if mediatype is not None:
                    self._check_uri_property(graph, dist_uri, 'http://www.w3.org/ns/dcat#mediaType',
                                             mediatype)

    def test_rdf_export_publisher(self):
        """Check that we get expected RDF data when exporting a publisher."""
        with self.admin_access.repo_cnx() as cnx:
            publisher = cnx.entity_from_eid(self.publisher_eid)
            publisher_uri = publisher.absolute_url()
            rdfpub = publisher.cw_adapt_to('RDFPrimary')
            graph = rdfio.default_graph()
            rdfpub.fill(graph)
            self._check_literal_property(graph, publisher_uri, 'http://xmlns.com/foaf/0.1/name',
                                         u'The Publisher')
            self._check_literal_property(graph, publisher_uri, 'http://xmlns.com/foaf/0.1/mbox',
                                         u'mailto:publisher@example.org')
            self._check_uri_property(graph, publisher_uri, 'http://purl.org/dc/terms/type',
                                     self.nat_concept_uri)

    def test_rdf_export_contact_point(self):
        """Check that we get expected RDF data when exporting a contact point."""
        with self.admin_access.repo_cnx() as cnx:
            contact = cnx.entity_from_eid(self.contact_eid)
            contact_uri = contact.absolute_url()
            rdfcontact = contact.cw_adapt_to('RDFContactPoint')
            graph = rdfio.default_graph()
            rdfcontact.fill(graph)
            self._check_literal_property(graph, contact_uri, 'http://www.w3.org/2006/vcard/ns#fn',
                                         u'The Contact Point')
            self._check_literal_property(graph, contact_uri,
                                         'http://www.w3.org/2006/vcard/ns#hasEmail',
                                         u'mailto:contact@example.org')

    def _check_literal_property(self, graph, subject_uri, rdf_property, expected_value):
        """Check that, in the given graph, `subject_uri` has the expected value for the
        `dcterms:title` property."""
        self.assertEqual(list(graph.objects(subject_uri, graph.uri(rdf_property))),
                         [expected_value])

    def _check_uri_property(self, graph, subject_uri, rdf_property, expected_uri):
        """Check that, in the given graph, `subject_uri` is related via `rdf_property` to a
        `foaf:Agent` with expected URI."""
        self.assertEqual(list(graph.objects(subject_uri, graph.uri(rdf_property))), [expected_uri])


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
