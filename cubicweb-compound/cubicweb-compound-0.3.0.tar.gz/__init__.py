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
"""cubicweb-compound application package

Library cube to handle assemblies of composite entities
"""

from functools import wraps

from cubicweb import neg_role
from cubicweb.schema import META_RTYPES, WORKFLOW_RTYPES, SYSTEM_RTYPES


def skip_meta(func):
    """Decorator to set `skiprtypes` and `skipetypes` parameters as frozensets
    including "meta" objects that should be implicitely ignored.
    """
    @wraps(func)
    def wrapped(*args, **kwargs):
        kwargs['skiprtypes'] = frozenset(
            set(kwargs.get('skiprtypes', ())) | META_RTYPES |
            WORKFLOW_RTYPES | SYSTEM_RTYPES)
        kwargs['skipetypes'] = frozenset(kwargs.get('skipetypes', ()))
        return func(*args, **kwargs)
    return wrapped


@skip_meta
def structure_def(schema, etype, skiprtypes=(), skipetypes=()):
    """Return the container structure with `etype` as root entity.

    This structure is a dictionary with entity types as keys and `(relation
    type, role)` as values. These entity types are reachable through composite
    relations from the root <etype>. Each key gives the name of an entity
    type, associated to a list of relation/role allowing to access to its
    parent (which may be the container or a contained).
    """
    graph = CompositeGraph(schema, skiprtypes=skiprtypes, skipetypes=skipetypes)
    return dict((child, set(relinfo))
                for child, relinfo in graph.parent_structure(etype).iteritems())


class CompositeGraph(object):
    """Represent a graph of entity types related through composite relations.

    A `CompositeGraph` can be used to iterate on schema objects through
    `parent_relations`/`child_relations` methods as well as on entities through
    `parent_related`/`child_related` methods.
    """

    @skip_meta
    def __init__(self, schema, skiprtypes=(), skipetypes=()):
        self.schema = schema
        self.skiprtypes = skiprtypes
        self.skipetypes = skipetypes

    def parent_relations(self, etype):
        """Yield composite relation information items walking the graph
        upstream from `etype`.

        These items are `(rtype, role), parents` where `parents` is a list of
        possible parent entity types reachable through `(rtype, role)`
        relation.
        """
        return self._composite_relations(etype, topdown=False)

    def child_relations(self, etype):
        """Yield composite relation information items walking the graph
        downstream from `etype`.

        These items are `(rtype, role), children` where `children` is a list of
        possible child entity types reachable through `(rtype, role)` relation.
        """
        return self._composite_relations(etype, topdown=True)

    def _composite_relations(self, etype, topdown):
        """Yield `(rtype, role), etypes` values corresponding to arcs of the
        graph of compositely-related entity types reachable from a `etype`
        entity type. `etypes` is a list of possible entity types reachable
        through `(rtype, role)` relation "upstream" (resp. "downstream") if
        `topdown` is True (resp. False).
        """
        try:
            eschema = self.schema[etype]
        except KeyError:
            return
        for rschema, teschemas, role in eschema.relation_definitions():
            if rschema.meta or rschema in self.skiprtypes:
                continue
            composite_role = role if topdown else neg_role(role)
            relation, children = (rschema.type, role), []
            for target in teschemas:
                if target in self.skipetypes:
                    continue
                rdef = rschema.role_rdef(eschema, target, role)
                if rdef.composite != composite_role:
                    continue
                children.append(target.type)
            if children:
                yield relation, children

    def parent_structure(self, etype, _visited=None):
        """Return the parent structure of the graph from `etype`.

        The structure is a dictionary mapping entity type in the graph with
        root `etype` to relation information allowing to walk the graph
        upstream from this entity type.
        """
        if _visited is None:
            _visited = set()
        structure = {}

        def update_structure(left, relation, right):
            structure.setdefault(left, {}).setdefault(relation, []).append(right)

        for (rtype, role), children in self.child_relations(etype):
            for child in sorted(children):
                update_structure(child, (rtype, neg_role(role)), etype)
                if child in _visited:
                    continue
                _visited.add(child)
                for left, rels in self.parent_structure(child, _visited).iteritems():
                    for relation, rights in rels.iteritems():
                        for right in rights:
                            update_structure(left, relation, right)
        return structure

    def parent_related(self, entity):
        """Yield information items on entities related to `entity` through
        composite relations walking the graph upstream from `entity`.

        These items are tuples `(child, (rtype, role), parent)` where `role` is
        the role of `child` entity in `rtype` relation with `parent`.
        """
        return self._composite_related(entity, False)

    def child_related(self, entity):
        """Yield information items on entities related to `entity` through
        composite relations walking the graph downstream from `entity`.

        These items are tuples `(parent, (rtype, role), child)` where `role` is
        the role of `parent` entity in `rtype` relation with `child`.
        """
        return self._composite_related(entity, True)

    def _composite_related(self, entity, topdown, _visited=None):
        """Yield arcs of the graph of compositely-related entities reachable
        from `entity`.

        An "arc" is a tuple `(l_entity, (rtype, role), r_entity)` where
        `l_entity` is a "parent" (resp. "child") entity when `topdown` is True
        (resp. False) and, conversely, `r_entity` is the "child" (resp.
        "parent") entity. `role` is always the role of `l_entity` in `rtype`
        relation.
        """
        if _visited is None:
            _visited = set()
        for (rtype, role), targettypes in self._composite_relations(
                entity.cw_etype, topdown):
            rset = entity.related(rtype, role=role, targettypes=targettypes)
            for target in rset.entities():
                yield entity, (rtype, role), target
                if target.eid in _visited:
                    continue
                _visited.add(target.eid)
                for x in self._composite_related(target, topdown, _visited):
                    yield x
