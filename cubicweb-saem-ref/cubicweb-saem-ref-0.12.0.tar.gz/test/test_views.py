# coding: utf-8
# copyright 2015-2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-saem-ref test for views."""

import json
import os
from datetime import date
from tempfile import NamedTemporaryFile
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from yams.schema import role_name

from cubicweb import Binary
from cubicweb.devtools.testlib import CubicWebTC
from cubicweb.web.views.actions import CopyAction

from cubes.skos.rdfio import default_graph

from cubes.saem_ref.views.widgets import process_incomplete_date

import testutils


class SetDateTC(unittest.TestCase):

    def test_set_date_month_beginning(self):
        self.assertEqual(date(1997, 6, 5), process_incomplete_date("5/6/1997"))
        self.assertEqual(date(1997, 6, 5), process_incomplete_date("5/6/97"))
        self.assertEqual(date(2012, 6, 5), process_incomplete_date("5/6/12"))
        self.assertEqual(date(1997, 6, 1), process_incomplete_date("6/1997"))
        self.assertEqual(date(1997, 1, 1), process_incomplete_date("1997"))
        # XXX: behavior has changed in dateutil with dayfirst=True
        # https://github.com/dateutil/dateutil/commit/2d42e046d55b9fbbc0a2f41ce83fb8ec5de2d28b
        self.assertIn(process_incomplete_date("1997/6/5"), [date(1997, 6, 5),  # dateutil<=2.5.1
                                                            date(1997, 5, 6),  # dateutil>=2.5.2
                                                            ])

    def test_set_date_month_end(self):
        self.assertEqual(date(1994, 8, 28), process_incomplete_date("28/08/1994", True))
        self.assertEqual(date(1994, 8, 31), process_incomplete_date("08/1994", True))
        self.assertEqual(date(1994, 2, 28), process_incomplete_date("1994/02", True))
        self.assertEqual(date(1994, 12, 31), process_incomplete_date("1994", True))

    def test_set_date_failure(self):
        with self.assertRaises(ValueError) as cm:
            process_incomplete_date("31/02/2012")
        self.assertIn("day is out of range for month", str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            process_incomplete_date("20/14/2015")
        self.assertIn("month must be in 1..12", str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            process_incomplete_date("20")


class FuncViewsTC(CubicWebTC):

    def test_xmlwrap_component(self):
        with self.admin_access.cnx() as cnx:
            bob = testutils.authority_record(cnx, u'bob')
            uri = cnx.create_entity('ExternalUri', uri=u'http://logilab.fr')
            cnx.create_entity('EACResourceRelation',
                              resource_relation_agent=bob,
                              resource_relation_resource=uri,
                              xml_wrap=Binary('<plip>plop</plip>'))
            cnx.commit()
        with self.admin_access.web_request() as req:
            rset = req.find('EACResourceRelation')
            component = self.vreg['ctxcomponents'].select(
                'saem_ref.xml_wrap', req, rset=rset)
            content = []
            component.render_body(content.append)
        self.assertIn(u'plop', content[0])
        self.assertEqual(content[0].count(u'plip'), 2)

    def test_citation_view(self):
        with self.admin_access.cnx() as cnx:
            bob = testutils.authority_record(cnx, u'bob')
            mandate = cnx.create_entity('Mandate', term=u'u',
                                        mandate_agent=bob)
            citation = cnx.create_entity('Citation',
                                         note=u'plop',
                                         reverse_has_citation=mandate)
            citation_uri = cnx.create_entity('Citation',
                                             note=u'plop',
                                             uri=u'http://pl.op/',
                                             reverse_has_citation=mandate)
            cnx.commit()
            without_link_html = citation.view('citation-link')
            with_link_html = citation_uri.view('citation-link')
            self.assertEqual(
                with_link_html,
                u'<a class="truncate" href="http://pl.op/" title="plop">plop</a>')
            self.assertEqual(without_link_html, u'<i class="truncate">plop</i>')

    def test_eac_import_user_has_no_naa(self):
        regid = 'saem_ref.eac-import'
        with self.admin_access.web_request() as req:
            output = self.view(regid, req=req, template=None)
            self.assertIn('be in an organization', output)
            self.assertIn('to access this functionnality', output)
        with self.admin_access.web_request() as req:
            authority = req.cnx.find('Organization', name=u'Default authority').one()
            req.user.cw_set(authority=authority)
            req.cnx.commit()
            output = self.view(regid, req=req, template=None)
            self.assertIn('have an NAA configured', output)
            self.assertIn('to access this functionnality', output)

    def test_eac_import_ok(self):
        regid = 'saem_ref.eac-import'
        fname = 'FRAD033_EAC_00001_simplified.xml'
        with self.admin_access.web_request() as req:
            req.user.cw_set(authority=testutils.authority_with_naa(req.cnx))
            naa = req.cnx.create_entity('ArkNameAssigningAuthority', who=u'EAC', what=1)
            # simply test the form properly render and is well formed
            self.view(regid, req=req, template=None)
            fields = {'file': (fname, open(self.datapath('EAC/' + fname))),
                      'naa': unicode(naa.eid)}
            req.form = self.fake_form(regid, fields)
            # now actually test the import
            req.view(regid)
            # test AuthorityRecord and Agent have been created, the former with a ARK from NAA
            # specified in form params, the Agent with a ARK from the user's NAA
            arecord = req.find('AuthorityRecord', name=u'Gironde. Conseil général').one()
            self.assertTrue(arecord.ark.startswith('1/'), arecord.ark)
            agent = req.find('Agent', name=u'Delphine Jamet').one()
            self.assertTrue(agent.ark.startswith('0/'), agent.ark)

    def test_eac_non_unique_isni(self):
        regid = 'saem_ref.eac-import'
        fname = 'FRAD033_EAC_00001_simplified.xml'
        with self.admin_access.client_cnx() as cnx:
            # ISNI is the same as the agent in EAC file.
            testutils.authority_record(cnx, u'bob', isni=u'22330001300016')
            cnx.commit()
            rset = cnx.find('AuthorityRecord')
            self.assertEqual(len(rset), 1)
        with self.admin_access.web_request() as req:
            req.user.cw_set(authority=testutils.authority_with_naa(req.cnx))
            # simply test the form properly render and is well formed
            self.view(regid, req=req, template=None)
            fields = {'file': (fname, open(self.datapath('EAC/' + fname))),
                      'naa': unicode(req.user.naa.eid)}
            req.form = self.fake_form(regid, fields)
            # now actually test the import
            html = req.view(regid)
            self.assertIn('EAC import failed', html)
            # Still only one AuthorityRecord.
            rset = req.find('AuthorityRecord')
            self.assertEqual(len(rset), 1)

    def test_eac_invalid_xml(self):
        regid = 'saem_ref.eac-import'
        fname = 'invalid_xml.xml'
        with self.admin_access.web_request() as req:
            req.user.cw_set(authority=testutils.authority_with_naa(req.cnx))
            fields = {'file': (fname, open(self.datapath('EAC/' + fname))),
                      'naa': unicode(req.user.naa.eid)}
            req.form = self.fake_form(regid, fields)
            # now actually test the import
            html = req.view(regid)
            self.assertIn('Invalid XML file', html)

    def test_eac_missing_tag(self):
        regid = 'saem_ref.eac-import'
        fname = 'missing_tag.xml'
        with self.admin_access.web_request() as req:
            req.user.cw_set(authority=testutils.authority_with_naa(req.cnx))
            fields = {'file': (fname, open(self.datapath('EAC/' + fname))),
                      'naa': unicode(req.user.naa.eid)}
            req.form = self.fake_form(regid, fields)
            # now actually test the import
            html = req.view(regid)
            self.assertIn('Missing tag cpfDescription in XML file', html)

    def test_highlight_script_execution(self):
        with self.admin_access.client_cnx() as cnx:
            scheme = testutils.setup_scheme(cnx, u'my thesaurus')
            cnx.commit()
            url = scheme.absolute_url(highlight='toto')
        self.assertIn(
            '$(document).ready(function(){$("h1, h2, h3, h4, h5, table tbody td")'
            '.highlight("toto");});}',
            self.http_publish(url)[0])

    def test_highlight_on_rql_plain_text_search_same_etype(self):
        with self.admin_access.client_cnx() as cnx:
            # we need two concepts to get a list view
            scheme = testutils.setup_scheme(cnx, u'my thesaurus', u'toto', u'tata toto')
            concept = scheme.reverse_in_scheme[0]
            cnx.commit()
        url = 'http://testing.fr/cubicweb/view?rql=toto&__fromsearchbox=1&subvid=tsearch'
        html = self.http_publish(url)[0]
        self.assertIn(
            '<a href="http://testing.fr/cubicweb/%s?highlight=toto" title="">' % concept.eid,
            html)

    def test_skos_negociation(self):
        with self.admin_access.client_cnx() as cnx:
            scheme = cnx.create_entity('ConceptScheme', title=u'musique',
                                       ark_naa=testutils.naa(cnx))
            scheme.add_concept(u'pop')
            cnx.commit()
        with self.admin_access.web_request(headers={'Accept': 'application/rdf+xml'}) as req:
            result = self.app_handle_request(req, 'conceptscheme')
            with NamedTemporaryFile(delete=False) as fobj:
                try:
                    fobj.write(result)
                    fobj.close()
                    graph = default_graph()
                    graph.load('file://' + fobj.name, rdf_format='xml')
                finally:
                    os.unlink(fobj.name)

    def test_download_filename(self):
        with self.admin_access.web_request() as req:
            cnx = req.cnx
            agent = testutils.authority_record(cnx, u'jim')
            for ark, expected_filename in (
                (u"", "EAC_{0}.xml".format(agent.eid)),
                (u"ZZZ/4242", "EAC_ZZZ_4242.xml".format(agent.eid)),
            ):
                agent.cw_set(ark=ark)
                view = self.vreg['views'].select('saem_ref.eac', req, agent.as_rset())
                view.set_request_content_type()
                self.assertEqual(
                    view._cw.headers_out.getRawHeaders('content-disposition'),
                    ['attachment;filename="{0}"'.format(expected_filename)],
                )

    def test_agent_place_as_concept_view(self):
        with self.admin_access.web_request() as req:
            cnx = req.cnx
            agent_place = cnx.create_entity('AgentPlace', name=u"""çàè€É'"><$""")
            content = agent_place.view('saem.agent_place_as_concept')
            self.assertEqual(content,
                             u"<strong><span>çàè€É&#39;&quot;&gt;&lt;$</span></strong>")

    def test_listitem(self):
        with self.admin_access.web_request() as req:
            entity = req.create_entity('CWGroup', name=u'a')
            content = entity.view('saem.listitem', tabid='blah')
            self.assertIn(entity.view('oneline'), content)
            self.assertIn('__redirectparams=tab%3Dblah&amp', content)


class AuthorityRecordFormsTC(CubicWebTC):

    def test_no_copy_action(self):
        with self.admin_access.cnx() as cnx:
            testutils.authority_record(cnx, u'toto')
            cnx.commit()
        with self.admin_access.web_request() as req:
            rset = req.find('AuthorityRecord', name=u'toto')
            actions = self.pactionsdict(req, rset)
            self.assertNotIn(CopyAction, actions['moreactions'])

    def test_unrelated_authorityrecord(self):
        from cubes.saem_ref.views.authorityrecord import unrelated_authorityrecord
        with self.admin_access.cnx() as cnx:
            ar1 = testutils.authority_record(cnx, u'1').eid
            ar2 = testutils.authority_record(cnx, u'2').eid
            # ExternalUri should not appear in choices.
            cnx.create_entity('ExternalUri', uri=u'http://no-where')
            cnx.commit()
        with self.admin_access.web_request() as req:
            cls = self.vreg['etypes'].etype_class('HierarchicalRelation')(req)
            form = self.vreg['forms'].select('edition', req, entity=cls)
            field = form.field_by_name('hierarchical_parent', 'subject')
            choices = unrelated_authorityrecord(
                'hierarchical_parent', form, field)
            expected = [(u'1', unicode(ar1)), (u'2', unicode(ar2))]
            self.assertCountEqual(choices, expected)
        # Now with a __linkto.
        linkto = 'hierarchical_parent:{0}:subject'.format(ar2)
        with self.admin_access.web_request(__linkto=linkto) as req:
            cls = self.vreg['etypes'].etype_class('HierarchicalRelation')(req)
            form = self.vreg['forms'].select('edition', req, entity=cls)
            field = form.field_by_name('hierarchical_parent', 'subject')
            choices = unrelated_authorityrecord(
                'hierarchical_parent', form, field)
            expected = [(u'2', unicode(ar2))]
            self.assertCountEqual(choices, expected)
            field = form.field_by_name('hierarchical_child', 'subject')
            choices = unrelated_authorityrecord(
                'hierarchical_child', form, field)
            expected = [(u'1', unicode(ar1)), (u'2', unicode(ar2))]
            self.assertCountEqual(choices, expected)


class SEDANavigationTC(CubicWebTC):

    def test_breadcrumbs(self):
        with self.admin_access.cnx() as cnx:
            scheme = testutils.seda_scheme(
                cnx, u'seda_document_type_code', u'preferred', u'QWE')
            doctypecodevalue = scheme.reverse_in_scheme[0]
            doctypecode = cnx.create_entity(
                'SEDADocumentTypeCode',
                seda_document_type_code_value=doctypecodevalue)
            doc = cnx.create_entity('ProfileDocument',
                                    seda_document_type_code=doctypecode)
            profile = cnx.create_entity('SEDAProfile', ark_naa=testutils.naa(cnx))
            archobj = cnx.create_entity(
                'ProfileArchiveObject',
                seda_name=cnx.create_entity('SEDAName'),
                seda_parent=profile)
            cnx.commit()
        with self.admin_access.web_request() as req:
            archobj = req.entity_from_eid(archobj.eid)
            profile = req.entity_from_eid(profile.eid)
            doc = req.entity_from_eid(doc.eid)
            # ProfileDocument not related through seda_parent, breadcrumbs
            # leads to /sedalib.
            breadcrumbs = doc.cw_adapt_to('IBreadCrumbs').breadcrumbs()
            expected_breadcrumbs = [
                (u'http://testing.fr/cubicweb/sedalib', u'SEDA components'),
                doc,
            ]
            self.assertEqual(breadcrumbs, expected_breadcrumbs)
            # ProfileDocument has seda_parent, breadcrumbs leads to parents
            # (ProfileArchiveObject, SEDAProfile).
            doc.cw_set(seda_parent=archobj)
            req.cnx.commit()
            doc.cw_clear_all_caches()
            breadcrumbs = doc.cw_adapt_to('IBreadCrumbs').breadcrumbs()
            expected_breadcrumbs = [profile, archobj, doc]
            self.assertEqual(breadcrumbs, expected_breadcrumbs)


class SEDAFormsTC(CubicWebTC):

    def _build_seda_scheme(self, rtype_name, label_kind=u'preferred'):
        with self.admin_access.cnx() as cnx:
            labels = (u'pif', u'paf', u'pouf')
            testutils.seda_scheme(cnx, rtype_name, label_kind, *labels)
            cnx.commit()
        return labels

    def test_seda_document_type_code_vocabulary(self):
        """Check that we get correct values in the combo box for document type code."""
        labels = self._build_seda_scheme(u'seda_document_type_code')
        with self.admin_access.web_request() as req:
            doc = self.vreg['etypes'].etype_class('SEDADocumentTypeCode')(req)
            form = self.vreg['forms'].select('edition', req, entity=doc)
            field = form.field_by_name('seda_document_type_code_value', 'subject')
            form_labels = [label for label, _ in field.vocabulary(form)]
            self.assertCountEqual(labels, form_labels)

    def test_seda_file_type_code_vocabulary(self):
        """Check that we get correct values in the combo box for file type code."""
        labels = self._build_seda_scheme(u'seda_file_type_code',
                                         u'alternative')
        with self.admin_access.web_request() as req:
            doc = self.vreg['etypes'].etype_class('SEDAFileTypeCode')(req)
            form = self.vreg['forms'].select('edition', req, entity=doc)
            field = form.field_by_name('seda_file_type_code_value', 'subject')
            values = list(field.vocabulary(form))
            form_labels = [label for label, _ in values]
            self.assertCountEqual(form_labels, labels)

    def test_seda_character_set_code_vocabulary(self):
        """Check that we get correct values in the combo box for character set code."""
        labels = self._build_seda_scheme(u'seda_character_set_code',
                                         u'alternative')
        with self.admin_access.web_request() as req:
            doc = self.vreg['etypes'].etype_class('SEDACharacterSetCode')(req)
            form = self.vreg['forms'].select('edition', req, entity=doc)
            field = form.field_by_name('seda_character_set_code_value', 'subject')
            values = list(field.vocabulary(form))
            form_labels = [label for label, _ in values]
            self.assertCountEqual(form_labels, labels)

    def test_seda_get_related_version(self):
        """Check that we get correct results when asking for `draft`, `published`, `replaced`
        version of a profile."""
        with self.admin_access.web_request() as req:
            profile1 = testutils.publishable_profile(req, title=u'Profile 1')
            req.cnx.commit()
            profile1.cw_adapt_to('IWorkflowable').fire_transition('publish')
            req.cnx.commit()
            profile1.cw_clear_all_caches()
            profile2 = testutils.publishable_profile(req, title=u'Profile 2', seda_replace=profile1)
            req.cnx.commit()
            profile2.cw_adapt_to('IWorkflowable').fire_transition('publish')
            req.cnx.commit()
            profile2.cw_clear_all_caches()
            profile3 = testutils.publishable_profile(req, title=u'Profile 3', seda_replace=profile2)
            req.cnx.commit()
            profile3.cw_adapt_to('IWorkflowable').fire_transition('publish')
            req.cnx.commit()
            profile3.cw_clear_all_caches()
            profile4 = testutils.publishable_profile(req, title=u'Profile 4', seda_replace=profile3)
            req.cnx.commit()

            def unwrap_generator(gen):
                try:
                    return next(iter(gen))
                except StopIteration:
                    return None

            # Draft profile
            box4 = self.vreg['ctxcomponents'].select('saem.seda.relatedprofiles', req,
                                                     entity=profile4)
            self.assertEqual(unwrap_generator(box4.predecessor()).eid, profile3.eid)
            self.assertIsNone(unwrap_generator(box4.current_version(state=u'published')))
            self.assertIsNone(unwrap_generator(box4.current_version(state=u'draft')))
            # Published profile
            box3 = self.vreg['ctxcomponents'].select('saem.seda.relatedprofiles', req,
                                                     entity=profile3)
            self.assertEqual(unwrap_generator(box3.predecessor()).eid, profile2.eid)
            self.assertIsNone(unwrap_generator(box3.current_version(state=u'published')))
            self.assertEqual(unwrap_generator(box3.current_version(state=u'draft')).eid,
                             profile4.eid)
            # Deprecated profile
            box2 = self.vreg['ctxcomponents'].select('saem.seda.relatedprofiles', req,
                                                     entity=profile2)
            self.assertIsNone(unwrap_generator(box2.predecessor()))
            self.assertEqual(unwrap_generator(box2.current_version(state=u'published')).eid,
                             profile3.eid)
            self.assertEqual(unwrap_generator(box2.current_version(state=u'draft')).eid,
                             profile4.eid)
            # Older deprecated profile
            box1 = self.vreg['ctxcomponents'].select('saem.seda.relatedprofiles', req,
                                                     entity=profile1)
            self.assertIsNone(unwrap_generator(box1.predecessor()))
            self.assertEqual(unwrap_generator(box1.current_version(state=u'published')).eid,
                             profile3.eid)
            self.assertEqual(unwrap_generator(box1.current_version(state=u'draft')).eid,
                             profile4.eid)

    def test_seda_actions_notype_to_import(self):
        from cubes.saem_ref.views import seda

        with self.admin_access.web_request() as req:
            profile = testutils.setup_seda_profile(req)
            req.cnx.commit()
            profile._cw = req  # XXX
            actions = self.pactionsdict(req, profile.as_rset())
            self.assertIn(seda.SEDAImportProfileArchiveObjectAction, actions['moreactions'])
            self.assertNotIn(seda.SEDAImportProfileDocumentAction, actions['moreactions'])
            actions = self.pactionsdict(req, profile.archives[0].as_rset())
            self.assertIn(seda.SEDAImportProfileArchiveObjectAction, actions['moreactions'])
            self.assertIn(seda.SEDAImportProfileDocumentAction, actions['moreactions'])
        with self.new_access('anon').web_request() as req:
            profile = req.entity_from_eid(profile.eid)
            actions = self.pactionsdict(req, profile.as_rset())
            self.assertNotIn(seda.SEDAImportProfileArchiveObjectAction, actions['moreactions'])
            self.assertNotIn(seda.SEDAImportProfileDocumentAction, actions['moreactions'])

    def test_seda_actions_not_exportable(self):
        from cubes.saem_ref.views import seda

        with self.admin_access.web_request() as req:
            profile = req.create_entity('SEDAProfile', ark_naa=testutils.naa(req.cnx))
            req.cnx.commit()
            profile._cw = req  # XXX
            actions = self.pactionsdict(req, profile.as_rset())
            self.assertNotIn(seda.SEDA1DownloadAction, actions['moreactions'])
            self.assertNotIn(seda.SEDA02DownloadAction, actions['moreactions'])
            req.create_entity('ProfileArchiveObject',
                              seda_name=req.create_entity('SEDAName'),
                              seda_parent=profile)
            req.cnx.commit()
            profile.cw_clear_all_caches()
        with self.admin_access.web_request() as req:
            profile = req.entity_from_eid(profile.eid)
            actions = self.pactionsdict(req, profile.as_rset())
            self.assertIn(seda.SEDA1DownloadAction, actions['moreactions'])
            self.assertIn(seda.SEDA02DownloadAction, actions['moreactions'])


class SEDAComponentsImportTC(CubicWebTC):

    def test_seda_doimport_controller(self):
        """Test for 'saem_ref.seda.doimport' controller (called from JavaScript).
        """
        with self.admin_access.cnx() as cnx:
            scheme = testutils.seda_scheme(
                cnx, u'seda_document_type_code', u'preferred', u'QWE')
            doctypecodevalue = scheme.reverse_in_scheme[0]
            doctypecode = cnx.create_entity(
                'SEDADocumentTypeCode',
                seda_document_type_code_value=doctypecodevalue)
            doc = cnx.create_entity('ProfileDocument',
                                    user_cardinality=u'1',
                                    user_annotation=u'plop',
                                    seda_document_type_code=doctypecode)
            profile = cnx.create_entity('SEDAProfile', ark_naa=testutils.naa(cnx))
            archobj = cnx.create_entity(
                'ProfileArchiveObject',
                seda_name=cnx.create_entity('SEDAName'),
                seda_parent=profile)
            cnx.commit()
        params = dict(eid=archobj.eid, cloned=doc.eid)
        with self.admin_access.web_request(**params) as req:
            path, _ = self.expect_redirect_handle_request(
                req, 'saem_ref.seda.doimport')
            etype, eid = path.split('/')
            self.assertEqual(etype, 'ProfileArchiveObject'.lower())
            clone = req.execute('Any X WHERE X seda_parent P, P eid %(p)s',
                                {'p': eid}).one()
            self.assertEqual([x.eid for x in clone.seda_clone_of], [doc.eid])
            # Check that relationship targets have been copied.
            self.assertEqual(
                clone.seda_document_type_code[0].seda_document_type_code_value[0].eid,
                doctypecodevalue.eid)
            # Check that original entity attributes have been copied.
            self.assertEqual(clone.user_cardinality, u'1')
            self.assertEqual(clone.user_annotation, u'plop')


class ArkViewsTC(CubicWebTC):

    def test_ark_authority_record_creation(self):
        with self.admin_access.cnx() as cnx:
            org = testutils.authority_with_naa(cnx)
            naa_eid = org.ark_naa[0].eid
            cnx.commit()
        with self.admin_access.web_request() as req:
            akind = req.cnx.find('AgentKind', name=u'person').one()
            record = self.vreg['etypes'].etype_class('AuthorityRecord')(req)
            record.eid = 'A'
            fields = {
                role_name('name', 'subject'): u'007',
                role_name('ark', 'subject'): u'',
                role_name('agent_kind', 'subject'): str(akind.eid),
                role_name('ark_naa', 'subject'): str(naa_eid),
            }
            req.form = self.fake_form('edition', entity_field_dicts=[(record, fields)])
            eid = int(self.expect_redirect_handle_request(req)[0])
            record = req.cnx.entity_from_eid(eid)
            self.assertEqual(record.ark, u'0/r%09d' % eid)

    def test_ark_agent_creation(self):
        with self.admin_access.web_request() as req:
            org = testutils.authority_with_naa(req)
            agent = self.vreg['etypes'].etype_class('Agent')(req)
            agent.eid = 'A'
            fields = {role_name('name', 'subject'): u'007',
                      role_name('ark', 'subject'): u'',
                      role_name('authority', 'subject'): str(org.eid)}
            req.form = self.fake_form('edition', entity_field_dicts=[(agent, fields)])
            eid = int(self.expect_redirect_handle_request(req)[0])
            agent = req.cnx.entity_from_eid(eid)
            self.assertEqual(agent.ark, u'0/oa%09d' % eid)

    def test_ark_scheme_creation(self):
        with self.admin_access.web_request() as req:
            scheme = self.vreg['etypes'].etype_class('ConceptScheme')(req)
            scheme.eid = 'A'
            fields = {role_name('ark', 'subject'): u'',
                      role_name('ark_naa', 'subject'): unicode(testutils.naa(req.cnx).eid)}
            req.form = self.fake_form('edition', entity_field_dicts=[(scheme, fields)])
            eid = int(self.expect_redirect_handle_request(req)[0])
            scheme = req.cnx.entity_from_eid(eid)
            self.assertEqual(scheme.ark, u'0/v%09d' % eid)

    def test_ark_concept_creation_form(self):
        # test addition of a concept by specifying in_scheme in form
        with self.admin_access.web_request() as req:
            scheme = req.cnx.create_entity('ConceptScheme', ark_naa=testutils.naa(req.cnx))
            concept = self.vreg['etypes'].etype_class('Concept')(req)
            concept.eid = 'A'
            concept_fields = {role_name('in_scheme', 'subject'): str(scheme.eid),
                              role_name('ark', 'subject'): u''}
            label = self.vreg['etypes'].etype_class('Label')(req)
            label.eid = 'B'
            label_fields = {role_name('label', 'subject'): u'Hello',
                            role_name('label_of', 'subject'): 'A'}
            req.form = self.fake_form('edition', entity_field_dicts=[(concept, concept_fields),
                                                                     (label, label_fields)])
            eid = int(self.expect_redirect_handle_request(req)[0])
            concept = req.cnx.entity_from_eid(eid)
            self.assertEqual(concept.ark, u'0/c%09d' % eid)

    def test_ark_concept_creation_linkto(self):
        # test addition of a concept by specifying in_scheme with __linkto
        with self.admin_access.web_request() as req:
            scheme = req.cnx.create_entity('ConceptScheme', ark_naa=testutils.naa(req.cnx))
            concept = self.vreg['etypes'].etype_class('Concept')(req)
            concept.eid = 'A'
            concept_fields = {}
            label = self.vreg['etypes'].etype_class('Label')(req)
            label.eid = 'B'
            label_fields = {role_name('label', 'subject'): u'Goodby',
                            role_name('label_of', 'subject'): 'A'}
            req.form = self.fake_form('edition', entity_field_dicts=[(concept, concept_fields),
                                                                     (label, label_fields)])
            req.form['__linkto'] = 'in_scheme:%s:subject' % scheme.eid
            eid = int(self.expect_redirect_handle_request(req)[0])
            concept = req.cnx.entity_from_eid(eid)
            self.assertEqual(concept.ark, u'0/c%09d' % eid)

    def test_ark_url_rewrite(self):
        with self.admin_access.web_request() as req:
            rewriter = self.vreg['urlrewriting'].select('schemabased', req)
            _pmid, rset = rewriter.rewrite(req, u'/ark:/JoE/Dalton')
            self.assertEqual(rset.printable_rql(), 'Any X WHERE X ark "JoE/Dalton"')

    def test_ark_ws(self):
        with self.new_access('anon').web_request(headers={'Accept': 'application/json'},
                                                 method='POST') as req:
            # not authenticated
            result = self.app_handle_request(req, 'ark')
            self.assertEqual(json.loads(result),
                             [{'error': 'This service requires authentication.'}])
        with self.admin_access.web_request(headers={'Accept': 'application/json'}) as req:
            # authenticated but user has no authority
            result = self.app_handle_request(req, 'ark')
            self.assertEqual(json.loads(result),
                             [{'error': 'User is not associated to an authority.'}])
        with self.admin_access.web_request(headers={'Accept': 'application/json'}) as req:
            authority = testutils.authority_with_naa(req)
            req.user.cw_set(authority=authority)
            req.cnx.commit()
            # authenticated with authority, but noot using a POST
            result = self.app_handle_request(req, 'ark')
            self.assertEqual(json.loads(result),
                             [{'error': 'This service is only accessible using POST.'}])
        with self.admin_access.web_request(headers={'Accept': 'application/json'},
                                           method='POST') as req:
            # eventually
            result = self.app_handle_request(req, 'ark')
            self.assertEqual(json.loads(result),
                             [{'ark': '0/a000000001'}])

    def test_download_filename(self):
        with self.admin_access.web_request() as req:
            cnx = req.cnx
            record = testutils.authority_record(cnx, u'jim')
            for ark, expected_filename in (
                (u"", "EAC_{0}.xml".format(record.eid)),
                (u"ZZZ/4242", "EAC_ZZZ_4242.xml"),
            ):
                record.cw_set(ark=ark)
                view = self.vreg['views'].select('saem_ref.eac', req, record.as_rset())
                view.set_request_content_type()
                self.assertEqual(
                    view._cw.headers_out.getRawHeaders('content-disposition'),
                    ['attachment;filename="{0}"'.format(expected_filename)],
                )


if __name__ == '__main__':
    unittest.main()
