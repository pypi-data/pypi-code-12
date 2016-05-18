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
"""cubicweb-saem_ref unit tests for entities.container"""

from datetime import date

from cubicweb.devtools.testlib import CubicWebTC

from cubes.saem_ref.entities import container

import testutils


def sort_container(container_def):
    for k, v in container_def:
        yield k, sorted(v)


class ContainerTC(CubicWebTC):

    def test_agent_container(self):
        # line below should be copied from entities.container.registration_callback
        container_def = container.agent_container_def(self.schema)
        container_def = dict(sort_container(container_def))
        self.assertEqual(container_def,
                         {'Activity': [('generated', 'subject'), ('used', 'subject')],
                          'AgentFunction': [('function_agent', 'subject')],
                          'AgentPlace': [('place_agent', 'subject')],
                          'Citation': [('has_citation', 'object')],
                          'EACResourceRelation': [('resource_relation_agent', 'subject')],
                          'EACSource': [('source_agent', 'subject')],
                          'GeneralContext': [('general_context_of', 'subject')],
                          'History': [('history_agent', 'subject')],
                          'LegalStatus': [('legal_status_agent', 'subject')],
                          'Mandate': [('mandate_agent', 'subject')],
                          'Occupation': [('occupation_agent', 'subject')],
                          'PhoneNumber': [('phone_number', 'object')],
                          'PostalAddress': [('place_address', 'object')],
                          'Structure': [('structure_agent', 'subject')]})
        entity = self.vreg['etypes'].etype_class('Agent')(self)
        self.assertIsNotNone(entity.cw_adapt_to('IContainer'))
        self.assertIsNone(entity.cw_adapt_to('IContained'))

    def test_scheme_container(self):
        # line below should be copied from entities.container.registration_callback
        container_def = container.scheme_container_def(self.schema)
        container_def = dict(sort_container(container_def))
        self.assertEqual(container_def,
                         {'Activity': [('generated', 'subject'), ('used', 'subject')],
                          'Concept': [('in_scheme', 'subject')]})
        entity = self.vreg['etypes'].etype_class('ConceptScheme')(self)
        self.assertIsNotNone(entity.cw_adapt_to('IContainer'))
        self.assertIsNone(entity.cw_adapt_to('IContained'))

    def test_concept_container(self):
        # line below should be copied from entities.container.registration_callback
        container_def = container.concept_container_def(self.schema)
        container_def = dict(sort_container(container_def))
        self.assertEqual(container_def,
                         {'Activity': [('generated', 'subject'), ('used', 'subject')],
                          'Label': [('label_of', 'subject')]})
        entity = self.vreg['etypes'].etype_class('Concept')(self)
        self.assertIsNotNone(entity.cw_adapt_to('IContainer'))
        # Concept is both container and contained :
        self.assertIsNotNone(entity.cw_adapt_to('IContained'))

    def test_seda_profile_container(self):
        # line below should be copied from entities.container.registration_callback
        container_def = container.seda_profile_container_def(self.schema)
        container_def = dict(sort_container(container_def))
        self.assertEqual(container_def,
                         {'SEDACharacterSetCode': [('seda_character_set_code', 'object')],
                          'SEDADocumentTypeCode': [('seda_document_type_code', 'object')],
                          'ProfileArchiveObject': [('seda_parent', 'subject')],
                          'ProfileDocument': [('seda_parent', 'subject')],
                          'SEDAAccessRestrictionCode': [('seda_access_restriction_code', 'object')],
                          'SEDAAppraisalRule': [('seda_appraisal_rule', 'object')],
                          'SEDAAppraisalRuleCode': [('seda_appraisal_rule_code', 'object')],
                          'SEDAAppraisalRuleDuration': [('seda_appraisal_rule_duration', 'object')],
                          'SEDAContentDescription': [('seda_content_description', 'object')],
                          'SEDADate': [('seda_latest_date', 'object'),
                                       ('seda_oldest_date', 'object')],
                          'SEDADescription': [('seda_description', 'object')],
                          'SEDADescriptionLevel': [('seda_description_level', 'object')],
                          'SEDAFileTypeCode': [('seda_file_type_code', 'object')],
                          'SEDAKeyword': [('seda_keyword_of', 'subject')],
                          'SEDAName': [('seda_name', 'object')],
                          })
        entity = self.vreg['etypes'].etype_class('SEDAProfile')(self)
        self.assertIsNotNone(entity.cw_adapt_to('IContainer'))
        self.assertIsNone(entity.cw_adapt_to('IContained'))


class TreeTC(CubicWebTC):

    def test_agent_tree(self):
        tree_def = container.tree_def(self.schema, 'Agent',
                                      skiprtypes=['wf_info_for']).items()
        tree_def = dict(sort_container(tree_def))
        self.assertEqual(tree_def,
                         {'Activity': [],
                          'Agent': [('function_agent', 'object'),
                                    ('general_context_of', 'object'),
                                    ('generated', 'object'),
                                    ('history_agent', 'object'),
                                    ('legal_status_agent', 'object'),
                                    ('mandate_agent', 'object'),
                                    ('occupation_agent', 'object'),
                                    ('phone_number', 'subject'),
                                    ('place_agent', 'object'),
                                    ('resource_relation_agent', 'object'),
                                    ('source_agent', 'object'),
                                    ('structure_agent', 'object'),
                                    ('used', 'object')],
                          'AgentFunction': [('has_citation', 'subject')],
                          'AgentPlace': [('has_citation', 'subject'), ('place_address', 'subject')],
                          'Citation': [],
                          'EACResourceRelation': [],
                          'EACSource': [],
                          'GeneralContext': [('has_citation', 'subject')],
                          'History': [('has_citation', 'subject')],
                          'LegalStatus': [('has_citation', 'subject')],
                          'Mandate': [('has_citation', 'subject')],
                          'Occupation': [('has_citation', 'subject')],
                          'PhoneNumber': [],
                          'PostalAddress': [],
                          'Structure': []})

    def test_scheme_tree(self):
        tree_def = container.tree_def(self.schema, 'ConceptScheme',
                                      skiprtypes=['wf_info_for']).items()
        tree_def = dict(sort_container(tree_def))
        self.assertEqual(tree_def,
                         {'Activity': [],
                          'Concept': [('generated', 'object'),
                                      ('label_of', 'object'),
                                      ('used', 'object')],
                          'ConceptScheme': [('generated', 'object'),
                                            ('in_scheme', 'object'),
                                            ('used', 'object')],
                          'Label': []})

    def test_concept_container(self):
        tree_def = container.tree_def(self.schema, 'Concept').items()
        tree_def = dict(sort_container(tree_def))
        self.assertEqual(tree_def,
                         {'Activity': [],
                          'Concept': [('generated', 'object'),
                                      ('label_of', 'object'),
                                      ('used', 'object')],
                          'Label': []})

    def test_seda_profile_tree(self):
        tree_def = container.tree_def(self.schema, 'SEDAProfile',
                                      skiprtypes=['wf_info_for']).items()
        tree_def = dict(sort_container(tree_def))
        self.assertEqual(tree_def,
                         {'ProfileArchiveObject': [('seda_access_restriction_code', 'subject'),
                                                   ('seda_appraisal_rule', 'subject'),
                                                   ('seda_content_description', 'subject'),
                                                   ('seda_name', 'subject'),
                                                   ('seda_parent', 'object')],
                          'ProfileDocument': [('seda_character_set_code', 'subject'),
                                              ('seda_description', 'subject'),
                                              ('seda_document_type_code', 'subject'),
                                              ('seda_file_type_code', 'subject'),
                                              ],
                          'SEDADocumentTypeCode': [],
                          'SEDACharacterSetCode': [],
                          'SEDAAccessRestrictionCode': [],
                          'SEDAAppraisalRule': [('seda_appraisal_rule_code', 'subject'),
                                                ('seda_appraisal_rule_duration', 'subject')],
                          'SEDAAppraisalRuleCode': [],
                          'SEDAAppraisalRuleDuration': [],
                          'SEDAContentDescription': [('seda_description', 'subject'),
                                                     ('seda_description_level', 'subject'),
                                                     ('seda_keyword_of', 'object'),
                                                     ('seda_latest_date', 'subject'),
                                                     ('seda_oldest_date', 'subject')],
                          'SEDADate': [],
                          'SEDADescription': [],
                          'SEDADescriptionLevel': [],
                          'SEDAFileTypeCode': [],
                          'SEDAKeyword': [],
                          'SEDAName': [],
                          'SEDAProfile': [('seda_parent', 'object')]})
        entity = self.vreg['etypes'].etype_class('SEDAProfile')(self)
        self.assertIsNotNone(entity.cw_adapt_to('ITree'))

    def test_lib_document_unit(self):
        with self.admin_access.repo_cnx() as cnx:
            testutils.seda_scheme(cnx, u'seda_document_type_code', u'preferred', u'CDO')
            name = cnx.create_entity('SEDAName')
            ar = cnx.create_entity('ProfileArchiveObject', seda_name=name)
            name = cnx.create_entity('SEDAName')
            ar2 = cnx.create_entity('ProfileArchiveObject', seda_name=name, seda_parent=ar)
            dctv = testutils.concept(cnx, 'CDO')
            dct = cnx.create_entity('SEDADocumentTypeCode', seda_document_type_code_value=dctv)
            doc = cnx.create_entity('ProfileDocument', seda_document_type_code=dct, seda_parent=ar)
            cnx.commit()
            self.assertEqual(ar.cw_adapt_to('IContained').container, None)
            itree = ar.cw_adapt_to('ITree')
            self.assertEqual(itree.parent(), None)
            self.assertEqual(set(e.eid for e in itree.children()), set([ar2.eid, doc.eid]))
            itree = ar2.cw_adapt_to('ITree')
            self.assertEqual(itree.parent().eid, ar.eid)
            self.assertEqual(itree.children(), [])
            itree = doc.cw_adapt_to('ITree')
            self.assertEqual(itree.parent().eid, ar.eid)
            self.assertEqual(itree.children(), [])

    def test_lib_document_unit_clone(self):
        """Functional test for SEDA component clone."""
        with self.admin_access.repo_cnx() as cnx:
            name = cnx.create_entity('SEDAName')
            ar = cnx.create_entity('ProfileArchiveObject', seda_name=name)
            name = cnx.create_entity('SEDAName', value=u'pouet')
            cloned = cnx.create_entity('ProfileArchiveObject', seda_name=name, seda_parent=ar)
            cnx.commit()
            cnx.create_entity(cloned.cw_etype, user_annotation=u'clone',
                              seda_parent=ar, seda_clone_of=cloned)
            cnx.commit()
            rset = cnx.execute(
                'Any X WHERE X user_annotation "clone", X seda_parent P')
            self.assertTrue(rset)

    def test_seda_profile_clone(self):
        """Functional test for SEDA profile cloning."""
        with self.admin_access.repo_cnx() as cnx:
            today = date.today()
            transferring_agent, archival_agent = testutils.setup_seda_agents(cnx)
            profile = cnx.create_entity('SEDAProfile', seda_transferring_agent=transferring_agent,
                                        ark_naa=testutils.naa(cnx))
            content_description = cnx.create_entity(
                'SEDAContentDescription',
                seda_description_level=cnx.create_entity('SEDADescriptionLevel'),
                seda_oldest_date=cnx.create_entity('SEDADate', value=today))
            restriction_code = cnx.create_entity('SEDAAccessRestrictionCode')
            seda_name = cnx.create_entity('SEDAName', value=u'Archive Name')
            cnx.create_entity('ProfileArchiveObject', seda_name=seda_name, seda_parent=profile,
                              seda_content_description=content_description,
                              seda_access_restriction_code=restriction_code)
            cnx.commit()
            profile.cw_adapt_to('IWorkflowable').fire_transition('publish')
            cnx.commit()
            clone = cnx.create_entity('SEDAProfile', title=u'Clone', seda_replace=profile,
                                      ark_naa=testutils.naa(cnx))
            cnx.commit()
            # ark and cwuri should not have been copied
            self.assertNotEqual(clone.ark, profile.ark)
            self.assertNotEqual(clone.cwuri, profile.cwuri)
            # Everything else should have been copied
            rql = ('Any AO WHERE AO seda_name SN, NOT SN eid %(sn_eid)s, SN value %(sn_value)s, '
                   'AO seda_content_description CD, CD seda_description_level DL, '
                   'CD seda_oldest_date OD, OD value %(od)s, AO seda_access_restriction_code RC, '
                   'AO seda_parent X, X title "Clone", NOT X eid %(original_eid)s')
            rset = cnx.execute(rql, {'sn_eid': seda_name.eid, 'sn_value': u'Archive Name',
                                     'od': today, 'original_eid': profile.eid})
            self.assertTrue(rset)


if __name__ == '__main__':
    import unittest
    unittest.main()
