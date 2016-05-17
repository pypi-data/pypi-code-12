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
"""cubicweb-saem_ref application package

Référenciel de Système d'Archivage Électronique Mutualisé
"""

from functools import partial

from logilab.common.registry import objectify_predicate

from cubicweb import neg_role
from cubes.compound import CompositeGraph


# Composite graph definitions used in permissions setup.
PERMISSIONS_GRAPHS = dict.fromkeys(
    ('Agent', 'ConceptScheme', 'ProfileDocument', 'ProfileArchiveObject'),
    partial(CompositeGraph, skiprtypes=('generated', 'used')))

OUTER_RELATIVE_PERM_RELATIONS = set([
    'seda_file_type_code_value', 'seda_character_set_code_value',
    'seda_document_type_code_value', 'seda_appraisal_rule_code_value',
    'seda_access_restriction_code_value', 'seda_description_level_value',
    'seda_keyword_scheme', 'seda_keyword_value',
    # those are not outer but non-mandatory...
    'seda_parent', 'seda_oldest_date', 'seda_latest_date',
])


# EAC mappings

eactype_mapping = {'corporateBody': u'authority',
                   'person': u'person',
                   'family': u'family'}
eacmaintenancetype_mapping = {"created": u'create',
                              "revised": u'modify'}
# Order matters for this one in order to export correctly
eacaddress_mapping = [('StreetName', 'street'), ('PostCode', 'postalcode'), ('CityName', 'city')]


def optional_relations(schema, graph_structure):
    """Return a dict with optional relations information in a CompositeGraph.

    Keys are names of entity types in the graph for which a relation type has
    no mandatory (cardinality in '1+') relation definitions and values is a
    set of respective `(rtype, role)` tuples.
    """
    optionals = dict()
    for etype, relations in graph_structure.iteritems():
        for (rtype, role), targets in relations.iteritems():
            for target in targets:
                rdef = schema[rtype].role_rdef(etype, target, role)
                if rdef.role_cardinality(role) in '1+':
                    break
            else:
                optionals.setdefault(etype, set()).add((rtype, role))
    return optionals


def mandatory_rdefs(schema, graph_structure):
    """Yield non-optional relation definitions (and the role of the parent in
    the relation) in a graph structure.
    """
    visited = set()
    for etype, relations in graph_structure.iteritems():
        for (rtype, role), targets in relations.iteritems():
            for target in targets:
                rdef = schema[rtype].role_rdef(etype, target, role)
                if rdef in visited:
                    continue
                visited.add(rdef)
                if rdef.role_cardinality(role) in '1+':
                    yield rdef, neg_role(role)


def cwuri_url(entity):
    """Return an absolute URL for entity's cwuri, handling case where ark is directly used, and so
    URL should be generated from it.
    """
    cwuri = entity.cwuri
    if cwuri.startswith('ark:'):
        cwuri = entity._cw.build_url(cwuri)
    return cwuri


@objectify_predicate
def user_has_authority(cls, req, **kwargs):
    """Return 1 if the user is associated to an authority."""
    return len(req.user.authority)


@objectify_predicate
def user_has_naa(cls, req, **kwargs):
    """Return 1 if the user is associated to an authority with a NAA configured."""
    return 1 if req.user.naa is not None else 0
