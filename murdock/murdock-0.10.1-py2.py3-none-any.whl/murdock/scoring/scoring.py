# -*- coding: utf-8 -*-
#
#   This file is part of the Murdock project.
#
#   Copyright 2016 Malte Lichtner
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""
Module :mod:`murdock.scoring.scoring`
-------------------------------------

Specifies the Murdock scoring API. It provides the base classes
:class:`Scoring` for scoring functions, :class:`ScoringTerm` for scoring terms
employed by scoring functions and :class:`ScoringTermPart` for computationally
expensive parts used by more than one scoring term (e.g. distance matrices). A
list of implemented scoring modules is given :mod:`here <murdock.scoring>`.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future.utils import viewitems, viewvalues

import logging

import numpy

import murdock.config


log = logging.getLogger('scoring')


class ScoringError(Exception):
    pass


class Scoring(object):
    """Parent class for all scoring function classes.

    This class is used to calculate and store scores for a
    :class:`~murdock.tree.Node`, called :attr:`root` including all descendents
    (:attr:`~murdock.tree.Node.children`, grandchildren, ...).

    .. seealso:: A usage example can be found in :mod:`murdock.scoring.custom`.

    """
    def __init__(self, root=None):
        #: whether this instance is a deepcopy of another `Scoring` instance
        #: (e.g. used to suppress redundant log messages)
        self.copy = False
        #: list of tuples of dynamically interacting nodes (which change
        #: independently)
        self.interactions = []
        #: root node of the tree
        self.root = root
        #: name of the scoring function
        self.name = None
        #: list of :class:`ScoringTerm` instances
        self.terms = []

    def deepcopy(self, root=None, suffix=''):
        """Return new scoring instance of same type with deepcopied attributes.
        """
        if root is None:
            root = self.root
        new_scoring = self.__class__(root=root)
        new_scoring.copy = True
        new_scoring._deepcopy_setup(self, suffix=suffix)
        return new_scoring

    def total(self):
        return sum(_term.weighted() for _term in self.terms)

    def add_term(self, term):
        if term.scoring is not None:
            raise ScoringError(
                'This scoring term is already associated with another '
                '`Scoring` instance `%s`.' % term.scoring)
        term.scoring = self
        self.terms.append(term)
        return True

    def rescore(self, node=None):
        diff = 0
        if node is None:
            for interaction in self.interactions:
                diff += self.score(interaction)
        else:
            for interaction in self._get_interactions(node):
                diff += self.score(interaction)
        return diff

    def score(self, nodes):
        multiplicity = len(nodes)
        s = 0
        diff = 0
        # Collect required scoring term parts.
        termparts = {}
        for term in self.terms:
            if term.multiplicity != multiplicity:
                continue
            for tp_class in term.required:
                if tp_class not in termparts:
                    tp = tp_class()
                    termparts = tp.add_missing_termparts(nodes, termparts)
        # Update scoring term values.
        for term in self.terms:
            if term.multiplicity != multiplicity:
                continue
            if term.multiplicity == 2:
                if (
                        not term.intra and nodes[0].object_serial is
                        nodes[1].object_serial):
                    continue
                if (not term.inter and nodes[0].object_serial is not
                        nodes[1].object_serial):
                    continue
            diff -= term.weight * term.values[nodes]
            term.values[nodes] = term.get_score(nodes, termparts)
            s += term.weight * term.values[nodes]
        diff += s
        return diff

    def set_postdocking_scoring_terms(self):
        """Remove scoring terms only needed for docking, not for analysis.
        """
        terms = []
        for t in self.terms:
            if t.use_for_analysis:
                terms.append(t)
            else:
                log.debug(
                    'Scoring term `%s` removed for post-docking analysis.',
                    t.name)
        self.terms = terms
        self.rescore()
        return True

    def setup(self, parms, docking, name, copy):
        """Setup method which must be overwritten by each child.
        """
        raise NotImplementedError

    def residue_scores(self, node1, node2):
        res_dicts = node1.residue_data(node2)
        scores1 = {_res: 0.0 for _res in res_dicts[0]}
        scores2 = {_res: 0.0 for _res in res_dicts[1]}
        for r1, n1 in viewitems(res_dicts[0]):
            for r2, n2 in viewitems(res_dicts[1]):
                self._add_interaction((n1, n2))
                s = self.score((n1, n2))
                scores1[r1] += s
                scores2[r2] += s
        return scores1, scores2

    def init_interactions(self):
        """Initialise the list :attr:`interactions`.
        """
        multiplicities = []
        for term in self.terms:
            if term.multiplicity not in multiplicities:
                multiplicities.append(term.multiplicity)
        self.interactions = []
        # Add single nodes to interactions for scores such as torsional stress.
        if 1 in multiplicities:
            for node in self.root.descendants():
                if not node.transforms:
                    continue
                interaction = (node, )
                self._add_interaction(interaction)
                self.score(interaction)
        # Add pairs of nodes to interactions for scores such as coulomb.
        if 2 in multiplicities:
            for leaf1 in self.root.leaves():
                for leaf2 in leaf1.unrelated():
                    if leaf1.static and not leaf2.static:
                        interaction = (leaf1, leaf2)
                    elif not leaf1.static and leaf2.static:
                        interaction = (leaf2, leaf1)
                    elif len(leaf1.atoms) <= len(leaf2.atoms):
                        interaction = (leaf1, leaf2)
                    else:
                        interaction = (leaf2, leaf1)
                    if interaction not in self.interactions:
                        self._add_interaction(interaction)
                        self.score(interaction)
        return True

    def _deepcopy_setup(self, template, suffix):
        return self.setup(
            template.parms, docking=template.docking,
            name='%s%s' % (template.name, suffix), copy=True)

    def _get_interactions(self, node):
        """Iterate over all :attr:`interactions` include `node`.
        """
        for interaction in self.interactions:
            if node in interaction:
                yield interaction
            for leaf in node.leaves():
                if leaf in interaction:
                    yield interaction
                    break

    def _add_interaction(self, interaction):
        self.interactions.append(interaction)
        for term in self.terms:
            if term.multiplicity == len(interaction):
                term.values[interaction] = 0
        return True


class ScoringTerm(object):
    """Parent class for terms in a scoring function.
    """

    def __init__(self):
        self.values = {}
        self.weight = None
        # :class:`Scoring` instance using this term
        self.scoring = None
        #: name of this term (to be referenced in results)
        self.name = self.__class__.__name__
        #: an (unweighted) offset score (e.g. a reference or an unbound score)
        self.offset = 0.

    @property
    def use_for_analysis(self):
        return True

    def setup(self, root, parameters):
        """General setup method to be overwritten by descendant scoring terms.

        The only parameter required for all scoring terms is attr:`weight`
        which has also to be set in any method overwriting this general method.

        """
        self.weight = parameters['weight']
        try:
            self.offset = parameters['offset']
        except KeyError:
            pass
        try:
            self.name = parameters['name']
        except KeyError:
            pass
        return True

    def weighted(self):
        return self.weight * self.unweighted()

    def unweighted(self):
        return sum(viewvalues(self.values)) + self.offset

    def get_score(self, nodes, args):
        """Return the unweighted score between all `nodes`.

        This method must be overwritten by any class based on this
        :class:`ScoringTerm` template to implement the actual (mathematical)
        form/fuction of the term.

        """
        raise NotImplementedError


class ScoringTermPart(object):

    def __init__(self):
        pass

    @property
    def required(self):
        # Return a tuple of `ScoringTermPart` classes required for evaluation.
        return tuple()

    def add_missing_termparts(self, nodes, termparts):
        for tp_class in self.required:
            if tp_class not in termparts:
                tp = tp_class()
                termparts = tp.add_missing_termparts(nodes, termparts)
        termparts[type(self)] = self.get_value(nodes, termparts)
        return termparts

    def get_value(self, nodes, termparts):
        raise NotImplementedError


class ConfigDeclaration(murdock.config.ConfigDeclaration):

    def scoring(self):
        """Configuration options for the scoring fuction/method used:

            - "module":
                scoring module to be used (must be compatible with the
                :mod:`~murdock.scoring` API) `(dtype=str, required=True)`

            - "parameters":
                parameters passed to the scoring module, e.g.
                :meth:`murdock.scoring.custom.ConfigDeclaration.\\
                parameters` `(dtype=dict, required=True)`

        """
        Option = murdock.config.ConfigOption
        opt = self.get_default_options()
        opt.append(Option(
            name='module', dtype=Option.string, description='python module '
            'containing the scoring function to be used'))
        opt.append(Option(
            name='parameters', dtype=dict, description='dictionary containing '
            'all parameters passed to the scoring function'))
        return opt
