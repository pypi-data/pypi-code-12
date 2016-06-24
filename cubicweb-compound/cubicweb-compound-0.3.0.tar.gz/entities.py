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
"""cubicweb-compound entity's classes

This module essentially provides adapters to handle a structure of composite
entities similarly to the container_ cube. The idea is to provide an API
allowing access to a root entity (the container) from any contained entities.

Assumptions:

* an entity may belong to one and only one container
* an entity may be both a container an contained

.. _container: https://www.cubicweb.org/project/cubicweb-container
"""

from logilab.common import deprecation

from cubicweb.view import EntityAdapter
from cubicweb.predicates import is_instance, partial_relation_possible

from cubes.compound import CompositeGraph

deprecator = deprecation.DeprecationManager("cubes.compound")
structure_def = deprecator.moved('0.3', 'cubes.compound', 'structure_def')


def copy_entity(original, **attributes):
    """Return a copy of an entity.

    Only attributes and non-composite relations are copied (relying on
    `entity.copy_relations()` for the latter).
    """
    attrs = attributes.copy()
    original.complete()
    for rschema in original.e_schema.subject_relations():
        if rschema.final and not rschema.meta:
            attr = rschema.type
            attrs.setdefault(attr, original.cw_attr_value(attr))
    clone = original._cw.create_entity(original.cw_etype, **attrs)
    clone.copy_relations(original.eid)
    return clone


class IContainer(EntityAdapter):
    """Abstract adapter for entities which are a container root."""
    __abstract__ = True
    __regid__ = 'IContainer'

    @classmethod
    def build_class(cls, etype):
        selector = is_instance(etype)
        return type(etype + 'IContainer', (cls,),
                    {'__select__': selector})

    @property
    def container(self):
        """For the sake of consistency with `IContained`, return the container to which this entity
        belongs (i.e. the entity wrapped by this adapter).
        """
        return self.entity

    @property
    def parent(self):
        """Returns the direct parent entity : always None in the case of a container.
        """
        return None


class IContained(EntityAdapter):
    """Abstract adapter for entities which are part of a container.

    This default implementation is purely computational and doesn't rely on any additional data in
    the model, beside a relation to go up to the direct parent.
    """
    __abstract__ = True
    __regid__ = 'IContained'
    _classes = {}
    parent_relations = None  # set this to a set of (rtype, role) in concret classes

    @classmethod
    def register_class(cls, vreg, etype, parent_relations):
        contained_cls = cls.build_class(etype, parent_relations)
        if contained_cls is not None:
            vreg.register(contained_cls)

    @classmethod
    def build_class(cls, etype, parent_relations):
        # check given parent relations
        for parent_relation in parent_relations:
            assert (isinstance(parent_relation, tuple) and
                    len(parent_relation) == 2 and
                    parent_relation[-1] in ('subject', 'object')), parent_relation
        # use already created class if any
        if etype in cls._classes:
            contained_cls = cls._classes[etype]
            # ensure registered class is the same at the one that would be generated
            assert contained_cls.__bases__ == (cls,)
            contained_cls.parent_relations |= parent_relations
            return None
        # else generate one
        else:
            selector = is_instance(etype)
            contained_cls = type(etype + 'IContained', (cls,),
                                 {'__select__': selector,
                                  'parent_relations': parent_relations})
            cls._classes[etype] = contained_cls
            return contained_cls

    @property
    def container(self):
        """Return the container to which this entity belongs, or None."""
        parent_relation = self.parent_relation()
        if parent_relation is None:
            # not yet attached to a parent
            return None
        parent = self.entity.related(*parent_relation, entities=True)[0]
        if parent.cw_adapt_to('IContainer'):
            return parent
        return parent.cw_adapt_to('IContained').container

    @property
    def parent(self):
        """Returns the direct parent entity if any, else None (not yet linked to our parent).
        """
        parent_relation = self.parent_relation()
        if parent_relation is None:
            return None  # not yet linked to our parent
        parent_rset = self.entity.related(*parent_relation)
        if parent_rset:
            return parent_rset.one()
        return None

    def parent_relation(self):
        """Return the relation used to attach this entity to its parent, or None if no parent is set
        yet.
        """
        for parent_relation in self.parent_relations:
            parents = self.entity.related(*parent_relation)
            assert len(parents) <= 1, 'more than one parent on %s: %s' % (self.entity, parents)
            if parents:
                return parent_relation
        return None


class IClonableAdapter(EntityAdapter):
    """Adapter for entity cloning.

    Concrete classes should specify `rtype` (and possible `role`) class
    attribute to something like `clone_of` depending on application schema.
    """
    __regid__ = 'IClonable'
    __abstract__ = True
    __select__ = partial_relation_possible()
    rtype, role = None, 'object'  # relation between the clone and the original.
    skiprtypes = ()
    skipetypes = ()
    clone_relations = {}  # registered relation type and role of the original entity.
    # hooks categories that should be activated during cloning
    enabled_hook_categories = ['metadata']

    @classmethod
    def __registered__(cls, *args):
        assert cls.rtype not in cls.clone_relations, '{} already registered for {}'.format(
            cls.__name__, cls.rtype)
        cls.clone_relations[cls.rtype] = cls.role
        return super(IClonableAdapter, cls).__registered__(*args)

    @property
    def graph(self):
        """The composite graph associated with this adapter."""
        return CompositeGraph(self._cw.vreg.schema,
                              skiprtypes=self.skiprtypes,
                              skipetypes=self.skipetypes)

    def clone_into(self, clone):
        """Recursivily clone the container graph of this entity into `clone`."""
        assert clone.cw_etype == self.entity.cw_etype, \
            "clone entity type {} does not match with original's {}".format(
                clone.cw_etype, self.entity.cw_etype)
        with self._cw.deny_all_hooks_but(*self.enabled_hook_categories):
            clone.copy_relations(self.entity.eid)
            clones = {self.entity: clone}
            for parent, (rtype, parent_role), child in self.graph.child_related(self.entity):
                rel = rtype if parent_role == 'object' else 'reverse_' + rtype
                kwargs = {rel: clones[parent]}
                clone = clones.get(child)
                if clone is not None:
                    clone.cw_set(**kwargs)
                else:
                    clones[child] = copy_entity(child, **kwargs)


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__)
    # Necessary during db-init or test mode.
    IClonableAdapter.clone_relations.clear()
    IContained._classes.clear()
