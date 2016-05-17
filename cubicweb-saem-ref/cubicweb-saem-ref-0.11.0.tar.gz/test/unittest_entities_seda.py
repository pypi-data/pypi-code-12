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
"""cubicweb-saem_ref unit tests for entities.seda"""

import re
from datetime import date

from lxml import etree

from yams import ValidationError

from cubicweb.devtools.testlib import CubicWebTC

from cubes.saem_ref import cwuri_url

import testutils


def sort_attrs(attrs_string):
    """
    >>> sort_attrs('name="listVersionID" fixed="edition 2009" type="xsd:token" use="required"')
    'fixed="edition 2009" name="listVersionID" type="xsd:token" use="required"'
    """
    return ' '.join(sorted(re.findall('[\w:]+="[^"]*"', attrs_string)))


class SEDAXSDExportTC(CubicWebTC):

    def setup_database(self):
        with self.admin_access.client_cnx() as cnx:
            profile = testutils.publishable_profile(
                cnx, title=u'my profile title &&', description=u'my profile description &&')
            for rtype, label, scheme_title in [
                (u'seda_description_level', u'file',
                 u'SEDA : Niveaux de description de contenu'),
                (u'seda_appraisal_rule_code', u'detruire', None),
                (u'seda_appraisal_rule_duration', u'P10Y', None),
                (u'seda_access_restriction_code', u'AR038', None),
                (u'seda_file_type_code', u'fmt/123', None),
                (u'seda_character_set_code', u'6', None),
                (u'seda_document_type_code', u'CDO', None),
            ]:
                testutils.seda_scheme(cnx, rtype, u'preferred', label,
                                      scheme_title=scheme_title)
            cnx.commit()
            archive = profile.archives[0]
            # Complete the basic content_description created in testutils.
            cd = archive.content_description
            file_concept = testutils.concept(cnx, 'file')
            cd.seda_description_level[0].cw_set(seda_description_level_value=file_concept)
            cd.cw_set(seda_latest_date=cnx.create_entity('SEDADate', value=date(2015, 2, 24)),
                      seda_oldest_date=cnx.create_entity('SEDADate'),
                      seda_description=cnx.create_entity('SEDADescription'))
            cnx.create_entity('SEDAKeyword', seda_keyword_of=cd,
                              seda_keyword_scheme=file_concept.scheme,
                              seda_keyword_value=file_concept)
            cnx.commit()
            # Add appraisal_rule attribute to the archive
            appraisal_code = cnx.create_entity('SEDAAppraisalRuleCode')
            appr_code = testutils.concept(cnx, 'detruire')
            appraisal_code.cw_set(seda_appraisal_rule_code_value=appr_code,
                                  user_annotation=u'detruire le document')
            appr_dur = testutils.concept(cnx, u'P10Y')
            appraisal_duration = cnx.create_entity('SEDAAppraisalRuleDuration',
                                                   seda_appraisal_rule_duration_value=appr_dur,
                                                   user_annotation=u"C'est dans 10ans je m'en irai")
            appraisal = cnx.create_entity('SEDAAppraisalRule',
                                          seda_appraisal_rule_code=appraisal_code,
                                          seda_appraisal_rule_duration=appraisal_duration)
            archive.cw_set(seda_appraisal_rule=appraisal)
            cnx.commit()
            # Add archive object
            ao_appraisal = cnx.create_entity(
                'SEDAAppraisalRule',
                seda_appraisal_rule_code=cnx.create_entity('SEDAAppraisalRuleCode'),
                seda_appraisal_rule_duration=cnx.create_entity('SEDAAppraisalRuleDuration'))
            ao_cd = cnx.create_entity(
                'SEDAContentDescription',
                seda_description_level=cnx.create_entity('SEDADescriptionLevel'))
            ar038 = testutils.concept(cnx, 'AR038')
            ar = cnx.create_entity('SEDAAccessRestrictionCode',
                                   seda_access_restriction_code_value=ar038,
                                   user_annotation=u'restrict')
            cnx.create_entity('ProfileArchiveObject',
                              seda_content_description=ao_cd,
                              seda_appraisal_rule=ao_appraisal,
                              seda_access_restriction_code=ar,
                              seda_name=cnx.create_entity('SEDAName'),
                              seda_parent=archive)
            cnx.commit()
            # Add minimal document and archive object
            file_type_code_value = testutils.concept(cnx, 'fmt/123')
            file_type_code = cnx.create_entity('SEDAFileTypeCode',
                                               user_cardinality=u'1',
                                               seda_file_type_code_value=file_type_code_value)
            character_set_code_value = testutils.concept(cnx, '6')
            character_set_code = cnx.create_entity(
                'SEDACharacterSetCode', user_cardinality=u'1',
                seda_character_set_code_value=character_set_code_value)
            document_type_code_value = testutils.concept(cnx, 'CDO')
            document_type_code = cnx.create_entity(
                'SEDADocumentTypeCode', seda_document_type_code_value=document_type_code_value)
            cnx.create_entity('ProfileDocument',
                              seda_description=cnx.create_entity('SEDADescription'),
                              seda_file_type_code=file_type_code,
                              seda_character_set_code=character_set_code,
                              seda_document_type_code=document_type_code,
                              seda_parent=archive)
            cnx.create_entity('ProfileArchiveObject',
                              seda_name=cnx.create_entity('SEDAName'),
                              seda_parent=archive)
            cnx.commit()
        self.profile_eid = profile.eid

    def test_seda_1_0(self):
        self._test_profile_xsd('SEDA-1.0.xsd', 'test_entities_seda_1.xml')

    def test_seda_0_2(self):
        self._test_profile_xsd('SEDA-0.2.xsd', 'test_entities_seda_02.xml')

    def _test_profile_xsd(self, adapter_id, expected_file):
        def repl(m):
            return '<{0} {1}{2}>'.format(m.group(1), sort_attrs(m.group(2)), m.group(3))

        with self.admin_access.client_cnx() as cnx:
            profile = cnx.entity_from_eid(self.profile_eid)
            generated_xsd = profile.cw_adapt_to(adapter_id).dump()
            # normalize attributes which are not in the same order (depending on the lxml.etree
            # version)
            generated_xsd = re.sub(r'<([\w:]+) ([^>]+?)(/?)>', repl, generated_xsd)
            with open(self.datapath('xsd', 'XMLSchema.xsd')) as xsd:
                xmlschema = etree.XMLSchema(etree.parse(xsd))
            xml = etree.fromstring(generated_xsd)
            xmlschema.assert_(xml)
            file_concept = testutils.concept(cnx, 'file')
            with open(self.datapath(expected_file)) as expected:
                self.assertMultiLineEqual(expected.read() %
                                          {'concept-uri': cwuri_url(file_concept),
                                           'scheme-ark': file_concept.scheme.ark,
                                           'scheme-uri': cwuri_url(file_concept.scheme)},
                                          generated_xsd)


class SEDATC(CubicWebTC):

    def test_incomplete_profile(self):
        with self.admin_access.client_cnx() as cnx:
            profile = testutils.setup_seda_profile(
                cnx, description=u'my profile description &&')
            cnx.commit()
            # ensure we can remove its first level document unit
            profile.archives[0].cw_delete()
            cnx.commit()
            # now we shouldn't be able to fire the publish transition
            with self.assertRaises(ValidationError):
                profile.cw_adapt_to('IWorkflowable').fire_transition('publish')

    def test_blockers(self):
        with self.admin_access.client_cnx() as cnx:
            profile = cnx.create_entity('SEDAProfile', ark_naa=testutils.naa(cnx))
            blockers = list(profile.cw_adapt_to('SEDA-1.0.xsd').blockers())
            self.assertEqual(blockers,
                             [(profile.eid, 'the profile should have at least a document unit')])
            self.assertFalse(profile.cw_adapt_to('SEDA-1.0.xsd').is_compatible())
            with cnx.deny_all_hooks_but():
                ao = cnx.create_entity('ProfileArchiveObject',
                                       user_cardinality=u'0..1',
                                       seda_name=cnx.create_entity('SEDAName'),
                                       seda_parent=profile)
            profile.cw_clear_all_caches()
            blockers = list(profile.cw_adapt_to('SEDA-1.0.xsd').blockers())
            expected = [
                (ao.eid, '0..1 and 0..n cardinalities are forbidden on first-level document unit'),
                (ao.eid, 'first level document unit must have a content description defined'),
                (ao.eid, 'first level document unit must have an access restriction defined'),
            ]
            self.assertEqual(blockers, expected)
            ao.cw_set(seda_content_description=cnx.create_entity(
                'SEDAContentDescription',
                user_cardinality=u'0..1',
                seda_description_level=cnx.create_entity('SEDADescriptionLevel')),
                seda_access_restriction_code=cnx.create_entity(
                    'SEDAAccessRestrictionCode', user_cardinality=u'0..1'),
                user_cardinality=u'1')
            ao.cw_clear_all_caches()
            blockers = list(profile.cw_adapt_to('SEDA-1.0.xsd').blockers())
            expected = [
                (ao.eid, '0..1 cardinality is not allowed on content description of a first-level document unit'),  # noqa
                (ao.eid, '0..1 cardinality is not allowed on access restriction of a first-level document unit'),  # noqa
            ]
            self.assertEqual(blockers, expected)


class ProfileDocumentTC(CubicWebTC):

    def test_profile_document_dctitle(self):
        with self.admin_access.client_cnx() as cnx:
            testutils.seda_scheme(cnx, u'seda_document_type_code', u'preferred', u'CDO',
                                  scheme_title=None)
            document_type_code_value = testutils.concept(cnx, u'CDO')
            document_type_code = cnx.create_entity(
                'SEDADocumentTypeCode', seda_document_type_code_value=document_type_code_value)
            document = cnx.create_entity('ProfileDocument',
                                         seda_document_type_code=document_type_code)
            self.assertEqual(document.user_annotation, None)
            self.assertEqual(document.dc_title(), 'CDO #%s' % document.eid)
            document.cw_attr_cache['user_annotation'] = 'hi there'
            self.assertEqual(document.dc_title(), 'hi there (CDO)')


if __name__ == '__main__':
    import unittest
    unittest.main()
