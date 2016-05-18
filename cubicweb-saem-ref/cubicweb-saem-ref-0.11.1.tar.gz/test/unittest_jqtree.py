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
"""cubicweb-saem_ref unit tests for jqTree view"""
import json

from cubicweb.devtools.testlib import CubicWebTC

import testutils


def profile_document(cnx, **kwargs):
    """Return a complete ProfileDocument"""
    for rtype, label in [
        (u'seda_file_type_code', u'fmt/123'),
        (u'seda_character_set_code', u'6'),
        (u'seda_document_type_code', u'CDO'),
    ]:
        testutils.seda_scheme(cnx, rtype, u'preferred', label)
    cnx.commit()
    file_type_code_value = testutils.concept(cnx, 'fmt/123')
    file_type_code = cnx.create_entity(
        'SEDAFileTypeCode', user_cardinality=u'1',
        seda_file_type_code_value=file_type_code_value)
    character_set_code_value = testutils.concept(cnx, '6')
    character_set_code = cnx.create_entity(
        'SEDACharacterSetCode', user_cardinality=u'1',
        seda_character_set_code_value=character_set_code_value)
    document_type_code_value = testutils.concept(cnx, 'CDO')
    document_type_code = cnx.create_entity(
        'SEDADocumentTypeCode',
        seda_document_type_code_value=document_type_code_value)
    return cnx.create_entity(
        'ProfileDocument',
        seda_description=cnx.create_entity('SEDADescription'),
        seda_file_type_code=file_type_code,
        seda_character_set_code=character_set_code,
        seda_document_type_code=document_type_code,
        **kwargs
    )


def json_entity(entity, load_on_demand=False, selected=None):
    """Helper returning the minimal JSON output of an entity."""
    data = {u'id': entity.eid}
    if load_on_demand:
        data[u'load_on_demand'] = True
    if selected:
        data[u'selected'] = selected
    return data


def ordered(jsobj):
    """Sort in place a JSON-like data structure."""
    if not jsobj:
        return
    if isinstance(jsobj, list):
        # only handle list with dicts inside.
        assert isinstance(jsobj[0], dict), jsobj
        jsobj.sort(key=lambda x: x['id'])
        for item in jsobj:
            ordered(item)
    elif isinstance(jsobj, dict):
        jsobj.pop('label', None)
        for item in jsobj.itervalues():
            ordered(item)


class JQTreeViewTC(CubicWebTC):

    def _setup(self):
        with self.admin_access.repo_cnx() as cnx:
            profile = cnx.create_entity('SEDAProfile', ark_naa=testutils.naa(cnx))
            archobj1 = cnx.create_entity('ProfileArchiveObject', seda_parent=profile,
                                         seda_name=cnx.create_entity('SEDAName'))
            document1 = profile_document(cnx, seda_parent=archobj1)
            archobj2 = cnx.create_entity('ProfileArchiveObject', seda_parent=profile,
                                         seda_name=cnx.create_entity('SEDAName'))
            cnx.commit()
            return profile, archobj1, document1, archobj2

    def assertJsonEqual(self, actual, expected):
        ordered(actual)
        ordered(expected)
        self.assertEqual(actual, expected)

    def test_json(self):
        """jqtree.json view for entity."""
        profile, archobj1, document1, archobj2 = self._setup()
        with self.admin_access.web_request() as req:
            # profile level
            profile = req.entity_from_eid(profile.eid)
            archobj1 = req.entity_from_eid(archobj1.eid)
            archobj2 = req.entity_from_eid(archobj2.eid)
            # selected is `profile`.
            expected = json_entity(profile, selected=profile.eid)
            expected[u'children'] = [
                # archobj1 has load_on_demand, because it has a child itself.
                json_entity(archobj1, load_on_demand=True),
                json_entity(archobj2),
            ]
            self.assertJsonEqual(json.loads(profile.view('jqtree.json')),
                                 [expected])
            # archive object level
            archobj1 = req.entity_from_eid(archobj1.eid)
            # selected is `archobj1`.
            expected = json_entity(profile, selected=archobj1.eid)
            expected[u'children'] = [
                # archobj1 has load_on_demand, because it has a child itself.
                json_entity(archobj1, load_on_demand=True),
                json_entity(archobj2),
            ]
            self.assertJsonEqual(json.loads(archobj1.view('jqtree.json')),
                                 [expected])
            # document level
            doc1 = req.entity_from_eid(document1.eid)
            # selected is `doc1`.
            expected = json_entity(profile, selected=doc1.eid)
            expected[u'children'] = [
                # archobj1 has not load_on_demand, because its child is also
                # returned.
                json_entity(archobj1, load_on_demand=False),
                json_entity(archobj2),
            ]
            # append child of `archobj1`
            expected['children'][0]['children'] = [json_entity(doc1)]
            self.assertJsonEqual(json.loads(doc1.view('jqtree.json')),
                                 [expected])

    def test_json_node(self):
        """jqtree.json view with "node=eid" (returns children)."""
        profile, archobj1, document1, archobj2 = self._setup()
        with self.admin_access.web_request() as req:
            def call_view(eid):
                req.form['node'] = str(eid)
                return req.view('jqtree.json')
            # profile level
            archobj1 = req.entity_from_eid(archobj1.eid)
            archobj2 = req.entity_from_eid(archobj2.eid)
            expected = [
                # archobj1 has load_on_demand, because it has a child itself.
                json_entity(archobj1, load_on_demand=True),
                json_entity(archobj2),
            ]
            self.assertJsonEqual(json.loads(call_view(profile.eid)),
                                 expected)
            # archive object level
            archobj1 = req.entity_from_eid(archobj1.eid)
            doc1 = req.entity_from_eid(document1.eid)
            expected = [
                json_entity(doc1),
            ]
            self.assertJsonEqual(json.loads(call_view(archobj1.eid)),
                                 expected)
            # document level
            expected = []
            self.assertJsonEqual(json.loads(call_view(doc1.eid)),
                                 expected)


if __name__ == '__main__':
    import unittest
    unittest.main()
