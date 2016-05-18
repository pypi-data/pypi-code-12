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
"""cubicweb-saem_ref unit tests for schema"""

import sqlite3
from datetime import date
from contextlib import contextmanager

from cubicweb import ValidationError, Unauthorized, neg_role
from cubicweb.devtools.testlib import CubicWebTC

from cubes.saem_ref import (PERMISSIONS_GRAPHS, mandatory_rdefs,
                            optional_relations)

import testutils


def graph_relations(schema, parent_structure):
    """Given a parent structure of a composite graph (and a schema object),
    return relation information `(rtype, role)` sets where `role` is the role
    of the child in the relation for the following kinds of relations:

    * structural relations,
    * optional relations (cardinality of the child not in '1*'),
    * mandatory relations (cardinality of the child in '1*').
    """
    def concat_sets(sets):
        """Concatenate sets"""
        return reduce(lambda x, y: x | y, sets, set())

    optionals = concat_sets(
        optional_relations(schema, parent_structure).values())
    mandatories = set([
        (rdef.rtype, neg_role(role))
        for rdef, role in mandatory_rdefs(schema, parent_structure)])
    structurals = concat_sets(map(set, parent_structure.values()))
    return structurals, optionals, mandatories


@contextmanager
def assertValidationError(self, cnx):
    with self.assertRaises(ValidationError) as cm:
        yield cm
        cnx.commit()
    cnx.rollback()


@contextmanager
def assertUnauthorized(self, cnx):
    with self.assertRaises(Unauthorized) as cm:
        yield cm
        cnx.commit()
    cnx.rollback()


def assertUnauthorizedRQL(self, cnx, rql):
    with assertUnauthorized(self, cnx):
        cnx.execute(rql)


class SchemaConstraintsTC(CubicWebTC):
    assertValidationError = assertValidationError

    def test_on_create_set_end_date_before_start_date(self):
        """ create an entity whose end_date is before start_date.
        ValidationError expected
        """
        with self.admin_access.repo_cnx() as cnx:
            with self.assertValidationError(cnx) as cm:
                testutils.agent(cnx, u'Arthur',
                                start_date=date(524, 02, 9), end_date=date(500, 07, 12))
            self.assertIn("must be less than", str(cm.exception))

    def test_on_update_set_end_date_before_start_date(self):
        """ create a valid entity and update it with a new end_date set before the start_date.
            ValidationError expected
        """
        if sqlite3.sqlite_version_info < (3, 7, 12):
            # with sqlite earlier than 3.7.12, boundary constraints are not checked by the database,
            # hence the constraint is only triggered on start_date modification
            self.skipTest('unsupported sqlite version')
        with self.admin_access.repo_cnx() as cnx:
            agent = testutils.agent(cnx, u'Arthur',
                                    start_date=date(454, 02, 9), end_date=date(475, 04, 12))
            cnx.commit()
            with self.assertValidationError(cnx) as cm:
                agent.cw_set(end_date=date(442, 07, 12))
            self.assertIn("must be less than", str(cm.exception))

    def test_on_update_set_start_date_after_end_date(self):
        """ create an entity without start_date :
            No constraint on the end_date
            update the entity with a start_date set after the start_date :
            ValidationError expected
        """
        with self.admin_access.repo_cnx() as cnx:
            agent = testutils.agent(cnx, u'Arthur', end_date=date(476, 02, 9))
            cnx.commit()
            with self.assertValidationError(cnx) as cm:
                agent.cw_set(start_date=date(527, 04, 12))
            self.assertIn("must be less than", str(cm.exception))

    def test_published_constraint_on_contact_point(self):
        """ create two agents: one published P and one not published N.
            create one more agent and check that interface will only show P that can become its
            contact point and archival agent
        """
        with self.admin_access.repo_cnx() as cnx:
            peter = testutils.agent(cnx, u'Peter', archival_roles=[u'archival'])
            testutils.agent(cnx, u'Norton', archival_roles=[u'archival'])
            cnx.commit()
            peter.cw_adapt_to('IWorkflowable').fire_transition('publish')
            agent = testutils.agent(cnx, u'Alice')
            cnx.commit()
            for rtype in ('archival_agent', 'contact_point'):
                rset = agent.unrelated(rtype, 'Agent')
                self.assertEqual(rset.one().eid, peter.eid)

    def test_agent_kind_person_on_contact_point(self):
        """Contact point choice is limited to person"""
        with self.admin_access.repo_cnx() as cnx:
            for name, kind in (
                (u"Mr Pink", u"person"),
                (u"Adams", u"family"),
                (u"Direction de la communication", u"authority"),
                (u"Ville de Bordeaux", u"authority"),
            ):
                agent = testutils.agent(cnx, name, kind)
                cnx.commit()
                agent.cw_adapt_to('IWorkflowable').fire_transition('publish')

            agent = cnx.find("Agent", name=u"Ville de Bordeaux").one()
            self.assertEqual(
                agent.unrelated("contact_point", "Agent").one(),
                cnx.find("Agent", name=u"Mr Pink").one(),
            )

    def test_agent_user_is_a_person(self):
        """Contact point choice is limited to person"""
        with self.admin_access.repo_cnx() as cnx:
            user = self.create_user(cnx, login=u'user', groups=('users',),
                                    authority=cnx.find('Authority').one())
            for name, kind in ((u'Mr Pink', u'person'),
                               (u'Adams', u'family'),
                               (u'Direction de la communication', u'authority')):
                agent = testutils.agent(cnx, name, kind)
            cnx.commit()
            for agent_name in (u'Adams', u'Direction de la communication'):
                agent = cnx.find('Agent', name=agent_name).one()
                with self.assertValidationError(cnx):
                    agent.cw_set(agent_user=user)
            agent = cnx.find('Agent', name=u'Mr Pink').one()
            agent.cw_set(agent_user=user)
            cnx.commit()

    def test_not_user_constraint_on_agent_related_list(self):
        """Create two agents on two distinct authority. Create one more agent and check that
        interface will only show consistent proposal for contact point and archival agent
        """
        with self.admin_access.repo_cnx() as cnx:
            # Create an archival agent in a custom authority
            authority = cnx.create_entity('Authority', name=u'boss club')
            jdoe = testutils.agent(cnx, u'jdoe', archival_roles=['archival'],
                                   authority=authority)
            # Create another archival agent in the default authority
            norton = testutils.agent(cnx, u'Norton', archival_roles=[u'archival'])
            cnx.commit()
            # Publish both agents (because of the published constraint)
            jdoe.cw_adapt_to('IWorkflowable').fire_transition('publish')
            norton.cw_adapt_to('IWorkflowable').fire_transition('publish')
            cnx.commit()
            # Now create a third agent and check the unrelated list
            agent = testutils.agent(cnx, u'Alice')
            cnx.commit()
            for rtype in ('archival_agent', 'contact_point'):
                rset = agent.unrelated(rtype, 'Agent')
                self.assertEqual(rset.one().eid, norton.eid)

    def test_agent_authority_consistency(self):
        with self.admin_access.repo_cnx() as cnx:
            authority1 = cnx.find('Authority').one()
            authority2 = cnx.create_entity('Authority', name=u'boss club')
            user = self.create_user(cnx, login=u'user', groups=('users',),
                                    authority=authority1)
            jdoe = testutils.agent(cnx, u'jdoe', authority=authority2)
            with self.assertValidationError(cnx):
                jdoe.cw_set(agent_user=user)


class AgentTC(CubicWebTC):
    assertUnauthorizedRQL = assertUnauthorizedRQL

    def test_fti(self):
        with self.admin_access.repo_cnx() as cnx:
            cnx.create_entity('AgentKind', name=u'Queen')
            agent = testutils.agent(cnx, u'Guenievre', kind=u'Queen', end_date=date(476, 02, 9))
            address = cnx.create_entity('PostalAddress', street=u"1 av. de l'europe",
                                        postalcode=u'31400', city=u'Toulouse')
            cnx.create_entity('AgentPlace', name=u'place', place_address=address, place_agent=agent)
            cnx.create_entity('AgentFunction', name=u'function', function_agent=agent)
            cnx.create_entity('LegalStatus', term=u'legal status', legal_status_agent=agent)
            cnx.commit()
            for search in (u'guenievre', u'europe', u'place', u'function', u'legal status'):
                self.set_description(search)
                # TODO: use subTest
                self.assertEqual(cnx.execute('Agent X WHERE X has_text %(search)s',
                                             {'search': search}).one().eid, agent.eid)

    def test_graph_structure(self):
        graph = PERMISSIONS_GRAPHS['Agent'](self.schema)
        expected = {
            'AgentFunction': {('function_agent', 'subject'): set(['Agent'])},
            'AgentPlace': {('place_agent', 'subject'): set(['Agent'])},
            'Citation': {('has_citation', 'object'): set([
                'GeneralContext', 'Mandate', 'Occupation', 'AgentFunction',
                'AgentPlace', 'History', 'LegalStatus',
            ])},
            'EACResourceRelation': {('resource_relation_agent', 'subject'): set(['Agent'])},
            'EACSource': {('source_agent', 'subject'): set(['Agent'])},
            'GeneralContext': {('general_context_of', 'subject'): set(['Agent'])},
            'History': {('history_agent', 'subject'): set(['Agent'])},
            'LegalStatus': {('legal_status_agent', 'subject'): set(['Agent'])},
            'Mandate': {('mandate_agent', 'subject'): set(['Agent'])},
            'Occupation': {('occupation_agent', 'subject'): set(['Agent'])},
            'PhoneNumber': {('phone_number', 'object'): set(['Agent'])},
            'PostalAddress': {('place_address', 'object'): set(['AgentPlace'])},
            'Structure': {('structure_agent', 'subject'): set(['Agent'])},
        }
        struct = dict(
            (k, dict((rel, set(targets)) for rel, targets in v.items()))
            for k, v in graph.parent_structure('Agent').items())
        self.assertEqual(struct, expected)

    def test_optional_relations(self):
        graph = PERMISSIONS_GRAPHS['Agent'](self.schema)
        structure = graph.parent_structure('Agent')
        opts = optional_relations(self.schema, structure)
        expected = {'Citation': set([('has_citation', 'object')])}
        self.assertEqual(opts, expected)

    def test_relations_consistency(self):
        graph = PERMISSIONS_GRAPHS['Agent'](self.schema)
        structure = graph.parent_structure('Agent')
        structurals, optionals, mandatories = graph_relations(
            self.schema, structure)
        self.assertEqual(structurals - optionals, mandatories)


class ConceptSchemeTC(CubicWebTC):

    def test_graph_structure(self):
        graph = PERMISSIONS_GRAPHS['ConceptScheme'](self.schema)
        expected = {
            'Concept': {('in_scheme', 'subject'): ['ConceptScheme']},
            'Label': {('label_of', 'subject'): ['Concept']},
        }
        self.assertEqual(graph.parent_structure('ConceptScheme'),
                         expected)

    def test_optional_relations(self):
        graph = PERMISSIONS_GRAPHS['ConceptScheme'](self.schema)
        opts = optional_relations(self.schema,
                                  graph.parent_structure('ConceptScheme'))
        expected = {}
        self.assertEqual(opts, expected)

    def test_relations_consistency(self):
        graph = PERMISSIONS_GRAPHS['ConceptScheme'](self.schema)
        structure = graph.parent_structure('ConceptScheme')
        structurals, optionals, mandatories = graph_relations(
            self.schema, structure)
        self.assertEqual(structurals - optionals, mandatories)


class SEDAProfileTC(CubicWebTC):
    assertValidationError = assertValidationError

    def test_fti(self):
        # "Reverse" text to be searched in order not to be troubled by other
        # entities that may live in the DB (e.g. Concepts) with similar text.
        with self.admin_access.client_cnx() as cnx:
            profile = testutils.setup_seda_profile(cnx)
            archive = profile.archives[0]
            archive.name.cw_set(value=u'profile name'[::-1])
            ac = archive.access_restriction_code
            ac.cw_set(user_annotation=u'some annotation'[::-1])
            testutils.seda_scheme(cnx, u'seda_document_type_code', u'preferred', u'CDO')
            seda_document_type_code_value = cnx.execute(
                'Concept X WHERE X preferred_label L, L label "CDO"').one()
            seda_document_type_code = cnx.create_entity(
                'SEDADocumentTypeCode',
                seda_document_type_code_value=seda_document_type_code_value)
            cnx.create_entity('ProfileDocument',
                              seda_description=cnx.create_entity(
                                  'SEDADescription',
                                  value=u'document description'[::-1]),
                              seda_document_type_code=seda_document_type_code,
                              seda_parent=archive)
            cnx.commit()
            for search in ('name', 'annotation', 'description'):
                self.set_description(search)
                rset = cnx.execute('Any X WHERE X has_text %(search)s',
                                   {'search': search[::-1]})
                # TODO: use subTest
                self.assertEqual([r for r, in rset.rows], [profile.eid])

    def test_graph_structure(self):
        graph = PERMISSIONS_GRAPHS['ProfileArchiveObject'](self.schema)
        expected = {
            'ProfileArchiveObject': {
                ('seda_parent', 'subject'): [
                    'SEDAProfile', 'ProfileArchiveObject']},
            'ProfileDocument': {
                ('seda_parent', 'subject'): ['ProfileArchiveObject']},
            'SEDAAccessRestrictionCode': {
                ('seda_access_restriction_code', 'object'): [
                    'ProfileArchiveObject']},
            'SEDAAppraisalRule': {
                ('seda_appraisal_rule', 'object'): ['ProfileArchiveObject']},
            'SEDAAppraisalRuleCode': {
                ('seda_appraisal_rule_code', 'object'): ['SEDAAppraisalRule']},
            'SEDAAppraisalRuleDuration': {
                ('seda_appraisal_rule_duration', 'object'): [
                    'SEDAAppraisalRule']},
            'SEDACharacterSetCode': {
                ('seda_character_set_code', 'object'): ['ProfileDocument']},
            'SEDAContentDescription': {
                ('seda_content_description', 'object'): [
                    'ProfileArchiveObject']},
            'SEDADate': {
                ('seda_latest_date', 'object'): ['SEDAContentDescription'],
                ('seda_oldest_date', 'object'): ['SEDAContentDescription']},
            'SEDADescription': {
                ('seda_description', 'object'): ['SEDAContentDescription',
                                                 'ProfileDocument']},
            'SEDADescriptionLevel': {
                ('seda_description_level', 'object'): [
                    'SEDAContentDescription']},
            'SEDADocumentTypeCode': {
                ('seda_document_type_code', 'object'): ['ProfileDocument']},
            'SEDAFileTypeCode': {
                ('seda_file_type_code', 'object'): ['ProfileDocument']},
            'SEDAKeyword': {
                ('seda_keyword_of', 'subject'): ['SEDAContentDescription']},
            'SEDAName': {
                ('seda_name', 'object'): ['ProfileArchiveObject']},
        }
        self.assertEqual(graph.parent_structure('SEDAProfile'),
                         expected)

    def test_optional_relations(self):
        graph = PERMISSIONS_GRAPHS['ProfileArchiveObject'](self.schema)
        opts = optional_relations(self.schema,
                                  graph.parent_structure('SEDAProfile'))
        expected = {
            'ProfileArchiveObject': set([('seda_parent', 'subject')]),
            'ProfileDocument': set([('seda_parent', 'subject')]),
            'SEDADate': set([('seda_oldest_date', 'object'),
                             ('seda_latest_date', 'object')]),
        }
        self.assertEqual(opts, expected)

    def test_relations_consistency(self):
        graph = PERMISSIONS_GRAPHS['ProfileArchiveObject'](self.schema)
        structure = graph.parent_structure('SEDAProfile')
        structurals, optionals, mandatories = graph_relations(
            self.schema, structure)
        self.assertEqual(structurals - optionals, mandatories)

    def _test_relative_permissions_through(self, permission):
        actual = [e.expression
                  for e in self.schema['ProfileArchiveObject'].permissions[permission]]
        expected = [
            u'NOT EXISTS(X seda_parent A), U in_group G, G name IN("managers", "users")',
            u'X seda_parent A, U has_update_permission A',
        ]
        self.assertEqual(actual, expected)
        actual = [e.expression
                  for e in self.schema['SEDADate'].permissions[permission]]
        expected = [
            'A seda_oldest_date X, U has_update_permission A',
            'A seda_latest_date X, U has_update_permission A',
        ]
        self.assertEqual(actual, expected)

    def test_relative_update_permissions_through(self):
        self._test_relative_permissions_through('update')

    def test_relative_delete_permissions_through(self):
        self._test_relative_permissions_through('delete')

    def test_relative_permissions_of(self):
        rdef = self.schema['seda_parent'].rdef('ProfileDocument', 'ProfileArchiveObject')
        rqlexpr, = rdef.permissions['add']
        self.assertEqual(rqlexpr.expression, 'U has_update_permission O')
        rdef = self.schema['seda_oldest_date'].rdef('SEDAContentDescription', 'SEDADate')
        rqlexpr, = rdef.permissions['delete']
        self.assertEqual(rqlexpr.expression, 'U has_update_permission S')

    def test_dates_constraints(self):
        with self.admin_access.client_cnx() as cnx:
            profile = testutils.setup_seda_profile(cnx)
            archive = profile.archives[0]
            desc = archive.content_description
            date = cnx.create_entity('SEDADate',
                                     reverse_seda_oldest_date=desc)
            cnx.commit()

            def assert_error(cm, date_type):
                self.assertEqual(cm.exception.errors,
                                 {'seda_%s_date-object' % date_type:
                                  u'SEDA date cannot be used as oldest and latest'})

            datetype = 'latest'
            self.set_description(datetype)
            with self.assertValidationError(cnx) as cm:
                desc.cw_set(seda_latest_date=date)
            assert_error(cm, datetype)
            desc.cw_set(seda_oldest_date=None)
            desc.cw_set(seda_latest_date=date)
            cnx.commit()
            datetype = 'oldest'
            self.set_description(datetype)
            with self.assertValidationError(cnx) as cm:
                desc.cw_set(seda_oldest_date=date)
            assert_error(cm, datetype)


class SEDAKeywordTC(CubicWebTC):
    assertValidationError = assertValidationError

    def test_scheme_value_constraint(self):
        with self.admin_access.client_cnx() as cnx:
            profile = testutils.setup_seda_profile(cnx)
            cnx.commit()
            cd = profile.archives[0].content_description
            naa = testutils.naa(cnx)
            unrelated_scheme = cnx.create_entity('ConceptScheme', ark_naa=naa)
            scheme = cnx.create_entity('ConceptScheme', ark_naa=naa)
            concept = scheme.add_concept(u'this')
            cnx.commit()
            with self.assertValidationError(cnx) as cm:
                kw = cnx.create_entity('SEDAKeyword', seda_keyword_of=cd)
                kw.cw_set(seda_keyword_value=concept)
                kw.cw_set(seda_keyword_scheme=unrelated_scheme)
            self.assertEqual(cm.exception.errors,
                             {'seda_keyword_value-subject':
                              u"concept doesn't belong to the scheme associated to the keyword"})

            kw = cnx.create_entity('SEDAKeyword', seda_keyword_of=cd)
            kw.cw_set(seda_keyword_value=concept,
                      seda_keyword_scheme=scheme)
            cnx.commit()


class SecurityTC(CubicWebTC):
    """Test case for permissions set in the schema"""
    assertUnauthorized = assertUnauthorized

    def test_agentkind_type(self):
        with self.admin_access.cnx() as cnx:
            kind = cnx.find('AgentKind', name=u'person').one()
            # no one can update nor delete a kind
            with self.assertRaises(Unauthorized):
                kind.cw_set(name=u'gloups')
                cnx.commit()
            cnx.rollback()
            with self.assertRaises(Unauthorized):
                kind.cw_delete()
                cnx.commit()
            cnx.rollback()

    def test_agent_kind_relation(self):
        """Test we can only change kind from unknown to another."""
        with self.admin_access.repo_cnx() as cnx:
            agent = testutils.agent(cnx, u'bob', kind=u'unknown-agent-kind')
            cnx.commit()
            agent.cw_set(agent_kind=cnx.find('AgentKind', name=u'person').one())
            cnx.commit()
            with self.assertRaises(Unauthorized):
                agent.cw_set(agent_kind=cnx.find('AgentKind', name=u'authority').one())

    def test_authority_type(self):
        with self.admin_access.repo_cnx() as cnx:
            self.create_user(cnx, login=u'user', groups=('users',))
            cnx.commit()
        with self.new_access('user').client_cnx() as cnx:
            with self.assertUnauthorized(cnx):
                cnx.create_entity('Authority', name=u'dream team')

    def test_authority_relation(self):
        with self.admin_access.repo_cnx() as cnx:
            self.create_user(cnx, login=u'user', groups=('users',),
                             authority=cnx.find('Authority').one())
            agent = testutils.agent(cnx, u'user')
            authority = cnx.create_entity('Authority', name=u'dream team')
            cnx.commit()
            # even manager can't change an agent's authority
            with self.assertUnauthorized(cnx):
                agent.cw_set(authority=authority.eid)
        with self.new_access('user').client_cnx() as cnx:
            agent = cnx.entity_from_eid(agent.eid)
            # user can't change its own authority
            with self.assertUnauthorized(cnx):
                agent.cw_set(authority=authority.eid)
            # user can't create an agent in another authority than its own
            with self.assertUnauthorized(cnx):
                testutils.agent(cnx, u'new agent', authority=authority.eid)
            # though he can add an agent to its own authority
            testutils.agent(cnx, u'new agent')
            cnx.commit()

    def test_agent_user(self):
        with self.admin_access.repo_cnx() as cnx:
            user1 = self.create_user(cnx, login=u'user1', groups=('users',),
                                     authority=cnx.find('Authority').one())
            user2 = self.create_user(cnx, login=u'user2', groups=('users',),
                                     authority=cnx.find('Authority').one())
            agent = testutils.agent(cnx, u'user1', agent_user=user1)
            cnx.commit()
        with self.new_access('user1').client_cnx() as cnx:
            agent = cnx.entity_from_eid(agent.eid)
            # user can't change its own user
            with self.assertUnauthorized(cnx):
                agent.cw_set(agent_user=user2.eid)
            with self.assertUnauthorized(cnx):
                agent.cw_set(agent_user=None)
            # user can't create an agent and specify its associated user
            with self.assertUnauthorized(cnx):
                testutils.agent(cnx, u'user2', agent_user=user2.eid)
            agent2 = testutils.agent(cnx, u'user2')
            cnx.commit()
            with self.assertUnauthorized(cnx):
                agent2.cw_set(agent_user=user2.eid)

    def test_agent_base(self):
        with self.admin_access.repo_cnx() as cnx:
            self.create_user(cnx, login=u'toto', groups=('users', 'guests'),
                             authority=cnx.find('Authority').one())
            cnx.commit()
        with self.new_access('toto').client_cnx() as cnx:
            function = cnx.create_entity('AgentFunction', name=u'grouillot')
            testutils.agent(cnx, u'bob', reverse_function_agent=function)
            cnx.commit()
        with self.admin_access.repo_cnx() as cnx:
            cnx.execute('DELETE U in_group G WHERE U login "toto", G name "users"')
            cnx.commit()
        with self.new_access('toto').client_cnx() as cnx:
            agent = cnx.find('Agent', name=u'bob').one()
            with self.assertUnauthorized(cnx):
                agent.cw_set(name=u'bobby')
            with self.assertUnauthorized(cnx):
                agent.reverse_function_agent[0].cw_set(name=u'director')

    def test_agent_wf_permissions(self):
        with self.admin_access.repo_cnx() as cnx:
            self.create_user(cnx, login=u'toto', groups=('users', 'guests'),
                             authority=cnx.find('Authority').one())
            cnx.commit()
        with self.new_access('toto').client_cnx() as cnx:
            function = cnx.create_entity('AgentFunction', name=u'grouillot')
            agent = testutils.agent(cnx, u'bob', reverse_function_agent=function)
            cnx.commit()
            iwf = agent.cw_adapt_to('IWorkflowable')
            iwf.fire_transition('publish')
            cnx.commit()
            # we can still modify a published agent
            agent.cw_set(name=u'bobby')
            function.cw_set(name=u'director')
            cnx.commit()

    def test_update_root_badgroup(self):
        with self.admin_access.repo_cnx() as cnx:
            self.create_user(cnx, login=u'toto', groups=('users', 'guests'))
            cnx.commit()
        with self.new_access('toto').client_cnx() as cnx:
            testutils.publishable_profile(cnx, title=u'pp')
            cnx.commit()
        with self.admin_access.repo_cnx() as cnx:
            cnx.execute(
                'DELETE U in_group G WHERE U login "toto", G name "users"')
            cnx.commit()
        with self.new_access('toto').client_cnx() as cnx:
            profile = cnx.find('SEDAProfile', title=u'pp').one()
            with self.assertUnauthorized(cnx):
                profile.cw_set(title=u'qq')

    def test_update_child(self):
        with self.admin_access.repo_cnx() as cnx:
            self.create_user(cnx, login=u'toto', groups=('users', 'guests'),
                             authority=cnx.find('Authority').one())
            cnx.commit()
        with self.new_access('toto').client_cnx() as cnx:
            agent = testutils.agent(cnx, u'bob')
            function = cnx.create_entity('AgentFunction', name=u'boss',
                                         function_agent=agent)
            cnx.commit()
            # Draft -> OK.
            function.cw_set(name=u'grouyo')
            cnx.commit()
            cnx.create_entity('PhoneNumber', number=u'1234',
                              reverse_phone_number=agent)
            cnx.commit()
            iwf = agent.cw_adapt_to('IWorkflowable')
            iwf.fire_transition('publish')
            cnx.commit()
            # Published -> still OK for agent.
            agent.cw_set(name=u'big boss')
            cnx.commit()
            cnx.create_entity('PhoneNumber', number=u'5678',
                              reverse_phone_number=agent)
            cnx.commit()

    def test_sedaprofile_wf_permissions(self):
        with self.admin_access.repo_cnx() as cnx:
            profile = testutils.publishable_profile(cnx, title=u'pp')
            name = cnx.create_entity('SEDAName')
            profile_archive_obj = cnx.create_entity(
                'ProfileArchiveObject', seda_name=name, seda_parent=profile)
            cnx.commit()
            # Profile in draft, modifications are allowed.
            profile.cw_set(title=u'ugh')
            cnx.commit()
            name.cw_set(value=u'argh')
            cnx.commit()
            seda_date = cnx.create_entity('SEDADate')
            profile_archive_obj.content_description.cw_set(seda_oldest_date=seda_date)
            cnx.commit()
            # Profile published, no modification allowed.
            profile.cw_adapt_to('IWorkflowable').fire_transition('publish')
            cnx.commit()
            with self.assertUnauthorized(cnx):
                profile.cw_set(title=u'gloups')
            with self.assertUnauthorized(cnx):
                name.cw_set(value=u'zorglub')
            with self.assertUnauthorized(cnx):
                seda_date.cw_set(value=date.today())
            with self.assertUnauthorized(cnx):
                profile_archive_obj.content_description.cw_set(
                    seda_latest_date=cnx.create_entity('SEDADate'))
            with self.assertUnauthorized(cnx):
                seda_date.cw_delete()
            with self.assertUnauthorized(cnx):
                profile_archive_obj.cw_delete()

    def test_sedaprofile_no_parent_wf_permissions(self):
        with self.admin_access.repo_cnx() as cnx:
            name = cnx.create_entity('SEDAName')
            profile_archive_obj = cnx.create_entity(
                'ProfileArchiveObject', seda_name=name)
            cnx.commit()
            # document unit has no parent, modifications are allowed.
            name.cw_set(value=u'argh')
            cnx.commit()
        with self.new_access('anon').client_cnx() as cnx:
            name = cnx.entity_from_eid(name.eid)
            profile_archive_obj = cnx.entity_from_eid(profile_archive_obj.eid)
            with self.assertUnauthorized(cnx):
                name.cw_set(value=u'zorglub')
            with self.assertUnauthorized(cnx):
                profile_archive_obj.cw_set(user_annotation=u'zorglub')
            ar = cnx.create_entity('SEDAAccessRestrictionCode')
            profile_archive_obj.cw_set(seda_access_restriction_code=ar)
            with self.assertUnauthorized(cnx):
                pass  # exception raised by the commit done by the context manager
        with self.admin_access.repo_cnx() as cnx:
            profile_archive_obj = cnx.entity_from_eid(profile_archive_obj.eid)
            profile_archive_obj.cw_delete()
            cnx.commit()

    def test_conceptscheme_wf_permissions(self):
        with self.admin_access.cnx() as cnx:
            scheme = cnx.create_entity('ConceptScheme', ark_naa=testutils.naa(cnx))
            cnx.commit()
            # in draft, modifications are allowed.
            concept = scheme.add_concept(u'blah')
            cnx.commit()
            # published, can't modify existing content.
            scheme.cw_adapt_to('IWorkflowable').fire_transition('publish')
            cnx.commit()
            with self.assertUnauthorized(cnx):
                scheme.cw_set(description=u'plop')
            with self.assertUnauthorized(cnx):
                concept.preferred_label[0].cw_set(label=u'plop')
            # though addition of new concepts / labels is fine
            new_concept = scheme.add_concept(u'plop')
            cnx.commit()
            new_label = cnx.create_entity('Label', label=u'arhg', label_of=concept)
            cnx.commit()
            # while deletion is fine for label but not for concept nor scheme
            new_label.cw_delete()
            cnx.commit()
            with self.assertUnauthorized(cnx):
                scheme.cw_delete()
            with self.assertUnauthorized(cnx):
                new_concept.cw_delete()


if __name__ == '__main__':
    import unittest
    unittest.main()
