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
Module :mod:`murdock.scoring.rmsd`
----------------------------------

A scoring module extending :mod:`murdock.scoring.custom` by an RMSD weight.

This module can be used to test conformational search methods. The score
diverges to negative infinity for RMSD -> 0 (with a cutoff at RMSD = 0.1)
whereas for large RMSDs the score is not affected by the RMSD.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

import numpy

import murdock.config
import murdock.math
import murdock.misc
import murdock.scoring.pool
import murdock.scoring.custom


log = logging.getLogger('scoring.rmsd')


class Scoring(murdock.scoring.custom.Scoring):
    """Scoring class modulating the score using the ligand RMSD to reference.

    The score is calculated exactly as in :mod:`murdock.scoring.custom` and
    then multiplied by a factor of (1 - (x / RMSD)**2) where RMSD is the
    all-atom RMSD of the ligand to its reference structure (which must be
    given) and x is the `critical RMSD` below which the factor is dominated by
    the RMSD value.

    """

    def setup(self, parms, docking=None, name='rmsd', copy=False):
        self.rmsd_term = murdock.scoring.pool.Manual()
        self.rmsd_term.setup(name='RMSD', weight=1)
        self.rmsd_term.values = {self.root: 0}
        self.add_term(self.rmsd_term)
        self.crit_rmsd = parms['critical_rmsd']
        # currently stored total RMSD
        self.rmsd = None
        self.docking = docking
        self.update_rmsd()
        self.score_rmsd_term()
        return super(Scoring, self).setup(parms, docking, name, copy)

    def score(self, nodes, update_rmsd=True):
        diff1 = super(Scoring, self).score(nodes)
        if update_rmsd:
            self.update_rmsd()
        diff2 = self.score_rmsd_term()
        return diff1 + diff2

    def rescore(self, node=None):
        diff = 0
        if node is None:
            self.update_rmsd()
            for interaction in self.interactions:
                diff += self.score(interaction, update_rmsd=False)
        else:
            for interaction in self._get_interactions(node):
                diff += self.score(interaction)
        return diff

    def residue_scores(self, *args):
        return False, False

    def update_rmsd(self):
        self.rmsd = murdock.math.atoms_rmsd(
            self.root.atoms, self.docking.ref_root.atoms)
        return True

    def score_rmsd_term(self):
        before = self.rmsd_term.values[self.root]
        after = -80. * numpy.exp(-self.rmsd / self.crit_rmsd)
        self.rmsd_term.values = {self.root: after}
        return after - before


class ConfigDeclaration(murdock.scoring.pool.ConfigDeclaration):

    def parameters(self):
        """Configuration options for this custom scoring module:

            - "terms":
                dictionary of term names from the scoring term
                :class:`~murdock.scoring.pool.ConfigDeclaration` to
                be included in the scoring and their corresponding parameters
                `(dtype=dict, required=True)`

            - "critical_rmsd":
                RMSD value below which the RMSD dominates the score


        """
        Option = murdock.config.ConfigOption
        opt = self.get_default_options()
        opt.append(Option(
            name='terms', dtype=list, description='scoring terms from the '
            'pool to be included in the scoring function and their parameters',
            required=True))
        opt.append(Option(
            name='critical_rmsd', dtype=murdock.misc.float_gt_zero,
            description='RMSD value below which the RMSD dominates the score'))
        return opt

    def terms(self):
        return murdock.scoring.custom.ConfigDeclaration().terms()
