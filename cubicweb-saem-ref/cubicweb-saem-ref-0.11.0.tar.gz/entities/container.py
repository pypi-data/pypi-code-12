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
"""cubicweb-saem_ref "compound"-related functionalities."""
from warnings import warn

from cubicweb import neg_role
from cubicweb.rset import ResultSet
from cubicweb.predicates import is_instance
from cubicweb.entities.adapters import ITreeAdapter

from cubes.compound.entities import structure_def, IContainer, IContained


def agent_container_def(schema):
    """Define container for Agent"""
    return structure_def(schema, 'Agent').items()


def scheme_container_def(schema):
    """Define container for ConceptScheme"""
    skiprtypes = ('broader_concept', 'label_of')
    return structure_def(schema, 'ConceptScheme', skiprtypes=skiprtypes).items()


def concept_container_def(schema):
    """Define container for Concept"""
    return structure_def(schema, 'Concept').items()


def seda_profile_container_def(schema):
    """Define container for SEDAProfile"""
    return structure_def(schema, 'SEDAProfile').items()


class IContainedToITree(ITreeAdapter):
    """Map IContained adapters to ITree, additionaly configured with a list of relations leading to
    contained's children
    """

    children_relations = None  # list of (relation type, role) to get entity's children

    @classmethod
    def build_class(cls, etype, children_relations):
        selector = is_instance(etype)
        return type(etype + 'ITree', (cls,),
                    {'__select__': selector,
                     'children_relations': children_relations})

    @property
    def tree_relation(self):
        parent_relation = self.entity.cw_adapt_to('IContained').parent_relation()
        if parent_relation is None:
            return None
        return parent_relation[0]

    @property
    def child_role(self):
        parent_relation = self.entity.cw_adapt_to('IContained').parent_relation()
        if parent_relation is None:
            return None
        return parent_relation[1]

    def parent(self):
        if self.tree_relation is None:
            return None
        return super(IContainedToITree, self).parent()

    def children_rql(self):
        # XXX may have different shapes
        return ' UNION '.join('(%s)' % self.entity.cw_related_rql(rel, role)
                              for rel, role in self.children_relations)

    def _children(self, entities=True):
        if entities:
            res = []
        else:
            res = ResultSet([], '')
            res.req = self._cw
        for rel, role in self.children_relations:
            res += self.entity.related(rel, role, entities=entities)
        return res

    def different_type_children(self, entities=True):
        """Return children entities of different type as this entity.

        According to the `entities` parameter, return entity objects or the
        equivalent result set.
        """
        res = self._children(entities)
        etype = self.entity.cw_etype
        if entities:
            return [e for e in res if e.cw_etype != etype]
        return res.filtered_rset(lambda x: x.cw_etype != etype, self.entity.cw_col)

    def same_type_children(self, entities=True):
        """Return children entities of the same type as this entity.

        According to the `entities` parameter, return entity objects or the
        equivalent result set.
        """
        res = self._children(entities)
        etype = self.entity.cw_etype
        if entities:
            return [e for e in res if e.cw_etype == etype]
        return res.filtered_rset(lambda x: x.cw_etype == etype, self.entity.cw_col)

    def children(self, entities=True, sametype=False):
        """Return children entities.

        According to the `entities` parameter, return entity objects or the
        equivalent result set.
        """
        if sametype:
            return self.same_type_children(entities)
        else:
            return self._children(entities)


class IContainerToITree(IContainedToITree):
    """Map IContainer adapters to ITree, similarly to :class:`IContainedToITree` but considering
    parent as None
    """

    @classmethod
    def build_class(cls, etype, children_relations):
        selector = is_instance(etype)
        return type(etype + 'ITree', (cls,),
                    {'__select__': selector,
                     'children_relations': children_relations})

    def parent(self):
        return None


def tree_def(schema, etype, skiprtypes=(), skipetypes=()):
    """Return a dictionary {etype: [(relation type, role)]} which are reachable through composite
    relations from the root <etype>. Each key gives the name of an entity type, associated to a list
    of relation/role allowing to access to its children (which is expected to be a contained).
    """
    skiprtypes = frozenset(skiprtypes)
    skipetypes = frozenset(skipetypes)
    contained = {}
    if etype not in schema:
        # Would occur, e.g., during migration.
        warn('%s not found in schema, cannot build a tree' % etype,
             RuntimeWarning)
        return {}
    candidates = set([schema[etype]])
    while candidates:
        eschema = candidates.pop()
        assert eschema not in contained, (eschema.type, contained)
        contained[eschema.type] = set()
        for rschema, teschemas, role in eschema.relation_definitions():
            if rschema.meta or rschema in skiprtypes:
                continue
            for rdef in rschema.rdefs.itervalues():
                if rdef.composite != role:
                    continue
                target = getattr(rdef, neg_role(role))
                if target in skipetypes:
                    continue
                if target not in contained:
                    candidates.add(target)
                contained[eschema.type].add((rschema.type, role))
    return contained


NO_TREE_RTYPES = set(('seda_name', 'seda_description', 'seda_access_restriction_code',
                      'seda_appraisal_rule', 'seda_keyword_of', 'seda_description_level',
                      'seda_document_type_code', 'seda_file_type_code', 'seda_character_set_code',
                      'seda_content_description', 'seda_oldest_date', 'seda_latest_date',
                      'wf_info_for'))

PROFILE_CONTAINER_DEF = {}


def registration_callback(vreg):
    vreg.register(IContainer.build_class('Agent'))
    for etype, parent_relations in agent_container_def(vreg.schema):
        IContained.register_class(vreg, etype, parent_relations)
    vreg.register(IContainer.build_class('ConceptScheme'))
    for etype, parent_relations in scheme_container_def(vreg.schema):
        if etype == 'Concept':
            # XXX turn parent_relations to a list to ensure broader_concept is considered first
            parent_relations = list(parent_relations)
            parent_relations.insert(0, ('broader_concept', 'subject'))
        IContained.register_class(vreg, etype, parent_relations)
    vreg.register(IContainer.build_class('Concept'))
    for etype, parent_relations in concept_container_def(vreg.schema):
        IContained.register_class(vreg, etype, parent_relations)
    vreg.register(IContainer.build_class('SEDAProfile'))
    for etype, parent_relations in seda_profile_container_def(vreg.schema):
        PROFILE_CONTAINER_DEF[etype] = parent_relations
        IContained.register_class(vreg, etype, parent_relations)
    # additional ITree interface for seda profile elements
    for etype, children_relations in tree_def(vreg.schema, 'SEDAProfile',
                                              skiprtypes=NO_TREE_RTYPES).items():
        if etype == 'SEDAProfile':
            vreg.register(IContainerToITree.build_class(etype, children_relations))
        else:
            vreg.register(IContainedToITree.build_class(etype, children_relations))
