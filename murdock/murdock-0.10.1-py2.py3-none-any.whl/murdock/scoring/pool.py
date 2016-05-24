# -*- coding: utf-8 -*-
#
#   This file belongs to the MURDOCK project
#
#   Copyright (C) 2013 Malte Lichtner
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
#
"""
Module :mod:`scoring.pool`
--------------------------

Provides a collection of scoring terms to be used by scoring functions emloying
the Murdock scoring API.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

import numpy
import scipy.constants
import scipy.spatial

import murdock.config
import murdock.math
from murdock.molstruct import ATOM_PARAMETER_LIBRARY
from murdock.scoring import ScoringTerm, ScoringTermPart


log = logging.getLogger('scoring.pool')


class Manual(ScoringTerm):
    """A term to manually set all values and properties.

    This term is a special case where all values are controlled manually, so it
    should be used with care, e.g. if an external tool is used to calculate
    scores and values need to be read from a file.

    """

    @property
    def required(self):
        return tuple()

    @property
    def multiplicity(self):
        return None

    def setup(self, name, weight):
        self.weight = weight
        self.name = name
        return True


class Collision(ScoringTerm):
    """A term describing the hard-sphere collision of two atoms.
    """

    @property
    def required(self):
        return (DistMat, )

    @property
    def multiplicity(self):
        return 2

    def setup(self, root, parms):
        if not super(Collision, self).setup(root, parms):
            return False
        try:
            self.cutoff_factor = parms['softness']
        except KeyError:
            self.cutoff_factor = 0.5
        vdw_radii = ATOM_PARAMETER_LIBRARY.vdw_radii()
        for atom in root.atoms:
            if atom.vdw_radius is not None:
                continue
            try:
                atom.vdw_radius = vdw_radii[atom.element]
            except KeyError:
                if atom.name[0] in vdw_radii:
                    defel = atom.name[0]
                else:
                    defel = 'C'
                log.warning(
                    'No vdW-radius for atom %d (`%s`) found based on its '
                    'element `%s`. The default value for element `%s` '
                    '(%.1f A) will be used for all atoms with this element.',
                    atom.serial, atom.name, atom.element, defel,
                    vdw_radii[defel])
                atom.vdw_radius = vdw_radii[defel]
                vdw_radii[atom.element] = vdw_radii[defel]
        return True

    def get_score(self, nodes, termparts):
        distmat = termparts[DistMat]
        vdw1 = numpy.array(
            [_a.vdw_radius * self.cutoff_factor for _a in nodes[0].atoms])
        vdw2 = numpy.array(
            [_a.vdw_radius * self.cutoff_factor for _a in nodes[1].atoms])
        t1 = numpy.tile(vdw1, (vdw2.shape[0], 1)).T
        t2 = numpy.tile(vdw2, (vdw1.shape[0], 1))
        v = (t1 + t2 > distmat).sum()
        return float(v) if v else 0.


class InterCollision(Collision):
    """A term describing the hard-sphere collision between two molecules.
    """

    @property
    def inter(self):
        return True

    @property
    def intra(self):
        return False

    @property
    def use_for_analysis(self):
        return False


class IntraCollision(Collision):
    """A term describing the hard-sphere collision within a molecule.
    """

    @property
    def inter(self):
        return False

    @property
    def intra(self):
        return True


class Shape(ScoringTerm):
    """A term describing shape complementary in a simple form.

    This is a parent class for other shape terms.

    """

    @property
    def inter(self):
        return True

    @property
    def intra(self):
        return False

    @property
    def multiplicity(self):
        return 2

    @property
    def required(self):
        raise NotImplementedError

    def get_score(self, nodes, termparts):
        v = -termparts[self.required[0]].sum()
        return float(v) if v else 0.


class Shape1(Shape):
    """A term describing shape complementary in a simple form based on r^-1.

    For every atom pair ij with distance `r_ij`, the score is:

        `Score = - weight / r_ij`

    """

    @property
    def required(self):
        return (InvDistMat, )


class Shape2(Shape):
    """A term describing shape complementary in a simple form based on r^-2.

    For every atom pair ij with distance `r_ij`, the score is:

        `Score = - weight / r_ij**2`

    """

    @property
    def required(self):
        return (InvDistMat2, )


class Shape3(Shape):
    """A term describing shape complementary in a simple form based on r^-3.

    For every atom pair ij with distance `r_ij`, the score is:

        `Score = - weight / r_ij**3`

    """

    @property
    def required(self):
        return (InvDistMat3, )


class Shape4(Shape):
    """A term describing shape complementary in a simple form based on r^-4.

    For every atom pair ij with distance `r_ij`, the score is:

        `Score = - weight / r_ij**4`

    """

    @property
    def required(self):
        return (InvDistMat4, )


class Shape6(Shape):
    """A term describing shape complementary in a simple form based on r^-6.

    For every atom pair ij with distance `r_ij`, the score is:

        `Score = - weight / r_ij**6`

    """

    @property
    def required(self):
        return (InvDistMat6, )


class Shape8(Shape):
    """A term describing shape complementary in a simple form based on r^-8.

    For every atom pair ij with distance `r_ij`, the score is:

        `Score = - weight / r_ij**8`

    """

    @property
    def required(self):
        return (InvDistMat8, )


class Coulomb(ScoringTerm):
    """A term describing unscreened Coulomb interaction.

    For every atom pair ij with distance `r_ij` and partial charges `q_i` and
    `q_j` the score is:

        `Score = weight * q1 * q2 / r_ij`

    """

    @property
    def required(self):
        return (InvDistMat, )

    @property
    def multiplicity(self):
        return 2

    def setup(self, root, parms):
        if not super(Coulomb, self).setup(root, parms):
            return False
        try:
            self.inter = parms['inter']
        except KeyError:
            self.inter = True
        try:
            self.intra = parms['intra']
        except KeyError:
            self.intra = False
        for atom in root.atoms:
            if atom.part_charge is None:
                log.fatal(
                    'Can not use scoring term `Coulomb` to score `%s`, no '
                    'partial charge for atom %d (`%s`) found.', root.name,
                    atom.serial, atom.name)
                return False
        return True

    def get_score(self, nodes, termparts):
        invdistmat = termparts[InvDistMat]
        q1 = numpy.matrix(
            [_atom.part_charge for _atom in nodes[0].atoms])
        q2 = numpy.matrix(
            [_atom.part_charge for _atom in nodes[1].atoms]).T
        return float(numpy.dot(q1, numpy.dot(invdistmat, q2)))


class ScreenedCoulomb(ScoringTerm):
    """A term describing screened Coulomb interaction.

    References:

        * Conway et al., 1951
        * Mehler et al., 1984
        * Solmajer et al., 1991
        * Morris et al., 1996

    For every atom pair ij with distance `r_ij` and partial charges `q_i` and
    `q_j` the score is:

        * `Score = weight * q_i * q_j / r_ij / epsilon(r_ij)`
        * `epsilon(r_ij) = A + B / (1 + k * exp(-lambda * B * r_ij))`

    with:

        * `A = -8.5525`
        * `B = e0 - A`
        * `lambda = 0.003627`
        * `epsilon0 = 78.4` (bulk H2O at 25°C)
        * `k = 7.7839`

    """

    @property
    def required(self):
        return (DistMat, InvDistMat)

    @property
    def multiplicity(self):
        return 2

    def setup(self, root, parms):
        if not super(ScreenedCoulomb, self).setup(root, parms):
            return False
        try:
            self.inter = parms['inter']
        except KeyError:
            self.inter = True
        try:
            self.intra = parms['intra']
        except KeyError:
            self.intra = False
        for atom in root.atoms:
            if atom.part_charge is None:
                log.fatal(
                    'Can not use scoring term `Coulomb` to score `%s`, no '
                    'partial charge for atom %d (`%s`) found.', root.name,
                    atom.serial, atom.name)
                return False
        e0 = 78.4
        self.l = 0.003627
        self.k = 7.7839
        self.A = -8.5525
        self.B = e0 - self.A
        return True

    def get_score(self, nodes, termparts):
        distmat = termparts[DistMat]
        invdistmat = termparts[InvDistMat]
        q1 = numpy.matrix(
            [_atom.part_charge for _atom in nodes[0].atoms])
        q2 = numpy.matrix(
            [_atom.part_charge for _atom in nodes[1].atoms]).T
        pot = invdistmat / (
            self.A + self.B / (
                1 + self.k * numpy.exp(-self.l * self.B * distmat)))
        return float(numpy.dot(q1, numpy.dot(pot, q2)))


class Torque(ScoringTerm):

    @property
    def required(self):
        return tuple()

    @property
    def multiplicity(self):
        return 1

    def get_score(self, nodes, termparts):
        return float(numpy.sum(
            (_tf.state() / scipy.constants.pi)**2 for _tf in
            nodes[0].transforms if
            isinstance(_tf, murdock.transforms.BondRotation)))


class Torsional(ScoringTerm):
    """A scoring term adding a torque to rotatable bonds.

    Each rotatable bond torsional state `phi` is compared to the
    corresponding state `phi_0` in the input structure (`not` the reference
    structure) in the form:

        `Score = (phi - phi_0)**2`

    The bonds to be scored can be chosen using one of the parameters
    `include_bonds` or `exclude_bonds` which are lists of bond names (for those
    bonds the attribute `~/murdock.molstruct.Bond.name` must be set.

    Either choose a number of named bonds to be rotatable (`include_bonds`) or
    choose all named bonds leaving out a number of particular bonds
    (`exclude_bonds`). If either parameter is given, bonds without name are
    disregarded. If no parameter is given, all bonds are used.

    """

    @property
    def required(self):
        return tuple()

    @property
    def multiplicity(self):
        return 1

    def setup(self, root, parms):
        if not super(Torsional, self).setup(root, parms):
            return False
        if 'include_bonds' in parms and 'exclude_bonds' in parms:
            log.fatal(
                'The parameters `include_bonds` and `exclude_bonds` can not '
                'be used together. Check the documentation for this scoring '
                'term for details.')
            return False
        elif 'include_bonds' in parms:
            self.bondnames = set([
                _b.name for _b in root.bonds if _b.rotatable and _b.name is
                not None and _b.name in parms['include_bonds']])
        elif 'exclude_bonds' in parms:
            self.bondnames = set([
                _b.name for _b in root.bonds if _b.rotatable and _b.name is
                not None and _b.name not in parms['exclude_bonds']])
        else:
            self.bondnames = set([
                _b.name for _b in root.bonds if _b.rotatable])
        if not self.scoring.copy:
            if self.bondnames:
                log.info(
                    'The following rotatable bonds will be scored with weight '
                    '%.7f: %s.', self.weight, ', '.join(self.bondnames))
                if None in self.bondnames:
                    log.warning(
                        'There are unnamed rotatable bonds being scored. For '
                        'convenience, each bond should be named within the '
                        'function given in the `rotatable_bonds` section of '
                        'the configuration file.')
            else:
                log.info(
                    'No rotatable bonds selected for scoring term `%s`.',
                    self.name)
        return True

    def get_score(self, nodes, args):
        return float(numpy.sum(
            (murdock.math.angle_diff(_tf.state()) / scipy.constants.pi)**2 for
            _tf in nodes[0].transforms if
            isinstance(_tf, murdock.transforms.BondRotation) and _tf.bond.name
            in self.bondnames))


class DistMat(ScoringTermPart):

    @property
    def required(self):
        return tuple()

    def get_value(self, nodes, termparts):
        return murdock.math.distmat(nodes[0].atoms, nodes[1].atoms)


class InvDistMat(ScoringTermPart):

    @property
    def required(self):
        return (DistMat, )

    def get_value(self, nodes, termparts):
        return 1. / numpy.maximum(termparts[DistMat], 0.5)


class InvDistMat2(ScoringTermPart):

    @property
    def required(self):
        return (InvDistMat, )

    def get_value(self, nodes, termparts):
        return termparts[InvDistMat]**2


class InvDistMat3(ScoringTermPart):

    @property
    def required(self):
        return (InvDistMat, InvDistMat2)

    def get_value(self, nodes, termparts):
        return termparts[InvDistMat] * termparts[InvDistMat2]


class InvDistMat4(ScoringTermPart):

    @property
    def required(self):
        return (InvDistMat2, )

    def get_value(self, nodes, termparts):
        return termparts[InvDistMat2]**2


class InvDistMat6(ScoringTermPart):

    @property
    def required(self):
        return (InvDistMat2, InvDistMat4)

    def get_value(self, nodes, termparts):
        return termparts[InvDistMat2] * termparts[InvDistMat4]


class InvDistMat8(ScoringTermPart):

    @property
    def required(self):
        return (InvDistMat4, )

    def get_value(self, nodes, termparts):
        return termparts[InvDistMat4]**2


class ConfigDeclaration(murdock.config.ConfigDeclaration):
    """Configuration options for all scoring terms defined in this pool.
    """

    def _get_weighted_term_default_options(self):
        Option = murdock.config.ConfigOption
        opt = self.get_default_options()
        opt.append(Option(
            name='weight', dtype=Option.finitefloat,
            description='term weight within the scoring function'))
        opt.append(Option(
            name='name', dtype=Option.string, description='term name (used in '
            'results)', required=False))
        return opt

    def Coulomb(self):
        """Configuration options for the :class:`~murdock.scoring.pool.Coulomb`
        term:

            - "weight":
                term weight within the scoring function
                `(dtype=float, required=True)`

            - "inter":
                score interactions between molecules
                `(dtype=bool, default=True)`

            - "intra"
                score interactions within molecules
                `(dtype=bool, default=False)`

        """
        Option = murdock.config.ConfigOption
        opt = self._get_weighted_term_default_options()
        opt.append(Option(
            name='inter', dtype=bool,
            description='score interactions between molecules', default=True))
        opt.append(Option(
            name='intra', dtype=bool,
            description='score interactions within molecules', default=False))
        return opt

    def InterCollision(self):
        """Configuration options for the
        :class:`~murdock.scoring.pool.InterCollision` term:

            - "weight":
                term weight within the scoring function
                `(dtype=float, required=True)`

            - "softness':
                factor multiplied on the van-der-Waals radii of two atoms
                before checking for an overlap; the scoring penalty only
                applies in there is an overlap of the modified (usually
                reduced) radii `(dtype=float, default=0.5)`

        """
        Option = murdock.config.ConfigOption
        opt = self._get_weighted_term_default_options()
        opt.append(Option(
            name='softness', dtype=Option.float_gt_zero,
            description='factor multiplied on the van-der-Waals radii of two '
            'atoms before checking for overlap', default=0.5))
        return opt

    def ScreenedCoulomb(self):
        """Configuration options for the
        :class:`~murdock.scoring.pool.ScreenedCoulomb` term:

            - "weight":
                term weight within the scoring function
                `(dtype=float, required=True)`

            - "inter":
                score interactions between molecules
                `(dtype=bool, default=True)`

            - "intra"
                score interactions within molecules
                `(dtype=bool, default=False)`

        """
        Option = murdock.config.ConfigOption
        opt = self._get_weighted_term_default_options()
        opt.append(Option(
            name='inter', dtype=bool,
            description='score interactions between molecules', default=True))
        opt.append(Option(
            name='intra', dtype=bool,
            description='score interactions within molecules', default=False))
        return opt

    def Shape1(self):
        """Configuration options for the :class:`~murdock.scoring.pool.Shape1`
        term:

            - "weight":
                term weight within the scoring function
                `(dtype=float, required=True)`

        """
        return self._get_weighted_term_default_options()

    def Shape2(self):
        """Configuration options for the :class:`~murdock.scoring.pool.Shape2`
        term:

            - "weight":
                term weight within the scoring function
                `(dtype=float, required=True)`

        """
        return self._get_weighted_term_default_options()

    def Shape3(self):
        """Configuration options for the :class:`~murdock.scoring.pool.Shape3`
        term:

            - "weight":
                term weight within the scoring function
                `(dtype=float, required=True)`

        """
        return self._get_weighted_term_default_options()

    def Shape4(self):
        """Configuration options for the :class:`~murdock.scoring.pool.Shape4`
        term:

            - "weight":
                term weight within the scoring function
                `(dtype=float, required=True)`

        """
        return self._get_weighted_term_default_options()

    def Shape6(self):
        """Configuration options for the :class:`~murdock.scoring.pool.Shape6`
        term:

            - "weight":
                term weight within the scoring function
                `(dtype=float, required=True)`

        """
        return self._get_weighted_term_default_options()

    def Shape8(self):
        """Configuration options for the :class:`~murdock.scoring.pool.Shape8`
        term:

            - "weight":
                term weight within the scoring function
                `(dtype=float, required=True)`

        """
        return self._get_weighted_term_default_options()

    def Torque(self):
        """Configuration options for the
        :class:`~murdock.scoring.pool.Torque` term:

            - "weight":
                term weight within the scoring function
                `(dtype=float, required=True)`

        """
        return self._get_weighted_term_default_options()

    def Torsional(self):
        """Configuration options for the
        :class:`~murdock.scoring.pool.Torsional` term:

            - "weight":
                term weight within the scoring function
                `(dtype=float, required=True)`

            - "include_bonds":
                list of bond names to be scored `(dtype=list, required=False)`

            - "exclude_bonds":
                list of bond names not to be scored `(dtype=list,
                required=False)`

        """
        Option = murdock.config.ConfigOption
        opt = self._get_weighted_term_default_options()
        opt.append(Option(
            name='include_bonds', dtype=list, description='list of bond names '
            'to be scored', required=False, validate=False))
        opt.append(Option(
            name='exclude_bonds', dtype=list, description='list of bond names '
            'not to be scored', required=False, validate=False))
        return opt
