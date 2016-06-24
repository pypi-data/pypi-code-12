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
"""cubicweb-compound tests"""

from cubicweb.devtools.testlib import CubicWebTC

from cubes.compound import CompositeGraph
from cubes.compound.entities import IClonableAdapter, copy_entity
from cubes.compound.views import CloneAction


def sort_keys(dic):
    return dict((k, sorted(v)) for k, v in dic.items())


class CompositeGraphTC(CubicWebTC):

    def test_parent_relations_notinschema(self):
        graph = CompositeGraph(self.schema)
        self.assertEqual(list(graph.parent_relations('Oups')), [])

    def test_child_relations_notinschema(self):
        graph = CompositeGraph(self.schema)
        self.assertEqual(list(graph.parent_relations('Oups')), [])

    def test_parent_relations_singleton(self):
        graph = CompositeGraph(self.schema)
        rels = list(graph.parent_relations('OnlineAccount'))
        self.assertEqual(rels, [(('account', 'object'), ['Agent'])])

    def test_parent_relations_comment(self):
        graph = CompositeGraph(self.schema)
        rels = list(graph.parent_relations('Comment'))
        self.assertEqual(rels, [(('comments', 'subject'),
                                 ['Comment', 'Anecdote'])])

    def test_child_relations_comment(self):
        graph = CompositeGraph(self.schema)
        rels = list(graph.child_relations('Comment'))
        self.assertEqual(rels, [(('comments', 'object'), ['Comment'])])

    def test_child_relations_singleton(self):
        graph = CompositeGraph(self.schema)
        rels = list(graph.child_relations('OnlineAccount'))
        self.assertEqual(rels, [])

    def test_child_relations_multiple(self):
        graph = CompositeGraph(self.schema)
        rels = list(graph.parent_relations('Event'))
        self.assertCountEqual(rels,
                              [(('relates', 'object'), ['Anecdote']),
                               (('event', 'object'), ['Biography'])])

    def test_parent_structure_agent(self):
        graph = CompositeGraph(self.schema)
        structure = graph.parent_structure('Agent')
        expected = {
            'OnlineAccount': {
                ('account', 'object'): ['Agent'],
            },
            'Biography': {
                ('biography', 'object'): ['Agent'],
            },
            'Event': {
                ('event', 'object'): ['Biography'],
                ('relates', 'object'): ['Anecdote'],
            },
            'Anecdote': {
                ('event', 'object'): ['Biography'],
                ('narrated_by', 'subject'): ['Agent'],
            },
            'Comment': {
                ('comments', 'subject'): ['Anecdote', 'Comment'],
            },
        }
        self.assertEqual(structure, expected)

    def test_parent_structure_anecdote(self):
        graph = CompositeGraph(self.schema)
        structure = graph.parent_structure('Anecdote')
        expected = {
            'Event': {
                ('relates', 'object'): ['Anecdote'],
            },
            'Comment': {
                ('comments', 'subject'): ['Anecdote', 'Comment'],
            }
        }
        self.assertEqual(structure, expected)

    def test_parent_structure_leaf(self):
        graph = CompositeGraph(self.schema)
        structure = graph.parent_structure('OnlineAccount')
        self.assertEqual(structure, {})

    def test_parent_related_singleton(self):
        graph = CompositeGraph(self.schema)
        with self.admin_access.repo_cnx() as cnx:
            agent = cnx.create_entity('Agent')
            cnx.commit()
            self.assertEqual(list(graph.parent_related(agent)), [])

    def test_parent_related(self):
        graph = CompositeGraph(self.schema)
        with self.admin_access.repo_cnx() as cnx:
            agent = cnx.create_entity('Agent')
            account = cnx.create_entity('OnlineAccount', reverse_account=agent)
            bio = cnx.create_entity('Biography', reverse_biography=agent)
            event = cnx.create_entity('Event', reverse_event=bio)
            anecdote1 = cnx.create_entity('Anecdote', reverse_event=bio)
            anecdote2 = cnx.create_entity('Anecdote', reverse_event=bio, narrated_by=agent,
                                          relates=event)
            comment1 = cnx.create_entity('Comment', comments=anecdote1)
            comment2 = cnx.create_entity('Comment', comments=comment1)
            cnx.commit()
            self.set_description('OnlineAccount')
            entities_graph = list(graph.parent_related(account))
            expected = [
                (account, ('account', 'object'), agent),
            ]
            yield self.assertCountEqual, entities_graph, expected
            self.set_description('Anecdote')
            entities_graph = list(graph.parent_related(anecdote1))
            anecdote1_expected = expected = [
                (anecdote1, ('event', 'object'), bio),
                (bio, ('biography', 'object'), agent),
            ]
            yield self.assertCountEqual, entities_graph, expected
            self.set_description('Event')
            entities_graph = list(graph.parent_related(event))
            expected = [
                (event, ('event', 'object'), bio),
                (event, ('relates', 'object'), anecdote2),
                (anecdote2, ('event', 'object'), bio),
                (bio, ('biography', 'object'), agent),
                (anecdote2, ('narrated_by', 'subject'), agent),
            ]
            yield self.assertCountEqual, entities_graph, expected
            self.set_description('Comment')
            entities_graph = list(graph.parent_related(comment2))
            expected = [
                (comment2, ('comments', 'subject'), comment1),
                (comment1, ('comments', 'subject'), anecdote1),
            ] + anecdote1_expected
            yield self.assertCountEqual, entities_graph, expected

    def test_child_related_singleton(self):
        graph = CompositeGraph(self.schema)
        with self.admin_access.repo_cnx() as cnx:
            agent = cnx.create_entity('Agent')
            cnx.commit()
            self.assertEqual(list(graph.child_related(agent)), [])

    def test_child_related(self):
        graph = CompositeGraph(self.schema)
        with self.admin_access.repo_cnx() as cnx:
            agent = cnx.create_entity('Agent')
            account = cnx.create_entity('OnlineAccount', reverse_account=agent)
            bio = cnx.create_entity('Biography', reverse_biography=agent)
            event = cnx.create_entity('Event', reverse_event=bio)
            anecdote1 = cnx.create_entity('Anecdote', reverse_event=bio)
            anecdote2 = cnx.create_entity('Anecdote', reverse_event=bio, narrated_by=agent,
                                          relates=event)
            comment1 = cnx.create_entity('Comment', comments=anecdote1)
            comment2 = cnx.create_entity('Comment', comments=comment1)
            cnx.commit()
            self.set_description('Anecdote')
            entities_graph = list(graph.child_related(anecdote2))
            expected = anecdote2_expected = [
                (anecdote2, ('relates', 'subject'), event),
            ]
            yield self.assertCountEqual, entities_graph, expected
            self.set_description('Anecdote (1)')
            entities_graph = list(graph.child_related(anecdote1))
            expected = anecdote1_expected = [
                (anecdote1, ('comments', 'object'), comment1),
                (comment1, ('comments', 'object'), comment2),
            ]
            yield self.assertCountEqual, entities_graph, expected
            self.set_description('Agent')
            entities_graph = list(graph.child_related(agent))
            expected = [
                (agent, ('account', 'subject'), account),
                (agent, ('biography', 'subject'), bio),
                (bio, ('event', 'subject'), event),
                (bio, ('event', 'subject'), anecdote1),
                (bio, ('event', 'subject'), anecdote2),
                (agent, ('narrated_by', 'object'), anecdote2),
            ] + anecdote2_expected + anecdote1_expected
            yield self.assertCountEqual, entities_graph, expected


class ContainerStructureTC(CubicWebTC):

    def test_adapters(self):
        entity = self.vreg['etypes'].etype_class('Agent')(self)
        self.assertIsNotNone(entity.cw_adapt_to('IContainer'))
        self.assertIsNone(entity.cw_adapt_to('IContained'))
        entity = self.vreg['etypes'].etype_class('OnlineAccount')(self)
        self.assertIsNotNone(entity.cw_adapt_to('IContained'))
        entity = self.vreg['etypes'].etype_class('Group')(self)
        self.assertIsNone(entity.cw_adapt_to('IContained'))


def one(cnx, etype, **kwargs):
    return cnx.find(etype, **kwargs).one()


class ContainerAPITC(CubicWebTC):

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            agent = cnx.create_entity('Agent')
            cnx.create_entity('OnlineAccount', reverse_account=agent)
            cnx.commit()

    def test_container(self):
        with self.admin_access.repo_cnx() as cnx:
            agent = one(cnx, 'Agent')
            self.assertEqual(agent.cw_adapt_to('IContainer').container, agent)
            account = one(cnx, 'OnlineAccount')
            icontained = account.cw_adapt_to('IContained')
            self.assertEqual(icontained.container, agent)

    def test_parent_relations_direct(self):
        with self.admin_access.repo_cnx() as cnx:
            account = one(cnx, 'OnlineAccount')
            icontained = account.cw_adapt_to('IContained')
            self.assertEqual(icontained.parent_relations,
                             set([('account', 'object')]))
            self.assertEqual(icontained.parent_relation(), ('account', 'object'))

    def test_parent_relations_indirect(self):
        with self.admin_access.repo_cnx() as cnx:
            agent = one(cnx, 'Agent')
            bio = cnx.create_entity('Biography', reverse_biography=agent)
            event = cnx.create_entity('Event', reverse_event=bio)
            cnx.commit()
            icontained = event.cw_adapt_to('IContained')
            self.assertEqual(icontained.parent_relations,
                             set([('event', 'object'), ('relates', 'object')]))
            self.assertEqual(icontained.parent_relation(), ('event', 'object'))


class CloneTC(CubicWebTC):

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            self.create_user(cnx, u'georges')
            cnx.commit()

    def test_copy_entity(self):
        with self.admin_access.repo_cnx() as cnx:
            cnx.create_entity('Agent', name=u'bob')
            cnx.commit()
        with self.new_access(u'georges').repo_cnx() as cnx:
            bob = cnx.find('Agent').one()
            bob2 = copy_entity(bob)
            alice = copy_entity(bob, name=u'alice', knows=bob)
            cnx.commit()
            self.assertEqual(bob2.name, u'bob')
            self.assertEqual(alice.name, u'alice')
            self.assertEqual([x.eid for x in alice.knows], [bob.eid])
            self.assertEqual(alice.created_by[0].login, u'georges')
            self.assertEqual(bob2.created_by[0].login, u'georges')
            self.assertGreater(alice.creation_date, bob.creation_date)
            alice2 = copy_entity(alice)
            cnx.commit()
            alice2.cw_clear_all_caches()
            self.assertEqual(alice2.name, u'alice')
            self.assertEqual([x.eid for x in alice2.knows], [bob.eid])

    def test_clone_adapter_registered(self):
        self.assertEqual(IClonableAdapter.clone_relations,
                         {'clone_of': 'object'})

    def test_clone_simple(self):
        with self.admin_access.repo_cnx() as cnx:
            bob = cnx.create_entity('Agent', name=u'bob')
            alice_eid = cnx.create_entity(
                'Agent', name=u'alice', knows=bob).eid
            cnx.create_entity('OnlineAccount', reverse_account=bob)
            cnx.commit()
        with self.new_access(u'georges').repo_cnx() as cnx:
            bob = cnx.find('Agent', name=u'bob').one()
            clone = cnx.create_entity('Agent', name=u'bobby')
            bob.cw_adapt_to('IClonable').clone_into(clone)
            clone.cw_clear_all_caches()
            cnx.commit()
            self.assertEqual(clone.name, u'bobby')
            # Non-structural relation "knows" is just a shallow copy.
            self.assertEqual([x.eid for x in clone.knows], [alice_eid])
            # Recursive copy for structural relation "account".
            rset = cnx.execute(
                'Any CA WHERE C account CA, C eid %(clone)s,'
                '             NOT CA identity OA, O account OA,'
                '             O eid %(original)s',
                {'original': bob.eid, 'clone': clone.eid})
            self.assertTrue(rset)

    def test_clone_full(self):
        with self.admin_access.repo_cnx() as cnx:
            agent = cnx.create_entity('Agent', name=u'bob')
            cnx.create_entity('OnlineAccount', reverse_account=agent)
            bio = cnx.create_entity('Biography', reverse_biography=agent)
            cnx.create_entity('Event', reverse_event=bio)
            cnx.create_entity('Anecdote', reverse_event=bio)
            cnx.create_entity('Anecdote', reverse_event=bio, narrated_by=agent)
            cnx.commit()
        with self.new_access(u'georges').repo_cnx() as cnx:
            bob = cnx.find('Agent', name=u'bob').one()
            clone = cnx.create_entity('Agent', name=u'bobby')
            bob.cw_adapt_to('IClonable').clone_into(clone)
            clone.cw_clear_all_caches()
            cnx.commit()
            # Ensure all relation (to new entities) are present on the clone.
            rset = cnx.execute(
                'Any X WHERE X name "bobby", X account AC, X biography B,'
                '            B event E, E is Event, B event A, A narrated_by X')
            self.assertTrue(rset)

    def test_clone_action(self):
        with self.admin_access.web_request() as req:
            entity = req.create_entity('Agent', name=u'bob')
            req.cnx.commit()
            action = self.vreg['actions'].select('copy', req,
                                                 rset=entity.as_rset())
            self.assertIsInstance(action, CloneAction)

    @staticmethod
    def _clone_setup(cnx):
        """Setup a graph of entities to be cloned."""
        agent = cnx.create_entity('Agent', name=u'bob')
        cnx.create_entity('OnlineAccount', reverse_account=agent)
        bio = cnx.create_entity('Biography', reverse_biography=agent)
        cnx.create_entity('Event', reverse_event=bio)
        cnx.create_entity('Anecdote', reverse_event=bio)
        cnx.create_entity('Anecdote', reverse_event=bio, narrated_by=agent)
        return agent

    def test_clone_hook(self):
        with self.admin_access.repo_cnx() as cnx:
            self._clone_setup(cnx)
            cnx.commit()
        with self.new_access(u'georges').repo_cnx() as cnx:
            bob = cnx.find('Agent', name=u'bob').one()
            clone = cnx.create_entity('Agent', name=u'bobby', clone_of=bob)
            cnx.commit()
            clone.cw_clear_all_caches()
            # Ensure all relation (to new entities) are present on the clone.
            rset = cnx.execute(
                'Any X WHERE X name "bobby", X account AC, X biography B,'
                '            B event E, E is Event, B event A, A narrated_by X')
            self.assertTrue(rset)

    def test_clone_controller(self):
        with self.admin_access.repo_cnx() as cnx:
            original_eid = self._clone_setup(cnx).eid
            cnx.commit()
        with self.new_access(u'georges').web_request() as req:
            req.form['eid'] = original_eid
            self.app_handle_request(req, 'compound.clone')
            rset = req.execute(
                'Any X WHERE X clone_of O, O eid %s' % original_eid)
            self.assertTrue(rset)


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
