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
Module :mod:`murdock.custom.gags`
---------------------------------

A custom module for the handling of glycosaminoglycan (GAG) structures.

.. warning::

    This module is intended for the use within the Pisabarro group. It relies
    on an unpublished residue naming convention for sulfated GAGs.

Recommended configuration
~~~~~~~~~~~~~~~~~~~~~~~~~

These docking steps, scoring and search parameters are recommended for GAGs.

It is a two-step workflow with a global Particle Swarm with rotatable
glycosidic linkages and a local Monte-Carlo search with all bonds rotatable.
The  search is fairly extensive and should provide a good sampling for single
GAGs oligomers. The large number of particles in the Particle Swarm search can
be reduced significantly for simple systems, e.g. systems with a strong
attractive interaction between receptor and ligand with an easily accessible
binding site.

The scoring function is the sum of a hard-shell collision term, a Coulomb
potential, a Shape complementary term and a penalty for deviations of
rotatable angles from the initial input structure. The parameters are trained
on 21 representative GAG-protein complexes without water or ions.

.. note::

    The input ligand MUST be properly minimized so that the optimal torsional
    angles for the unbound GAG can be used as reference for the torsional
    term.

.. code-block:: java

    "steps": [
      {
        "title": "default",
        "scoring": {
          "module": "scoring.custom",
          "parameters": {
            "terms": {
              "InterCollision": {
                "weight": 100.0,
                "van_der_waals_radius_correction_factor": 0.5
              },
              "Coulomb": {
                "weight": 0.470
              },
              "Shape4": {
                "weight": 0.020
              },
              "Torsional": {
                "weight": 0.510
              }
            }
          }
        }
      },
      {
        "title": "global",
        "transforms": {
          "translation": {
            "scaling": 10.0
          },
          "rotation": {
            "scaling": 6.2830
          },
          "rotatable_bonds": {
            "scaling": 1.5708,
            "module": "custom.gags",
            "function": "get_glycosidic_bonds"
          }
        },
        "search": {
          "module": "search.ps",
          "parameters": {
            "initial_number_of_particles": 100,
            "particle_annihilation_interval": 10,
            "minimum_number_of_particles": 1,
            "maximum_initial_step": 1.0,
            "maximum_initial_velocity": 0.7,
            "particle_inertia": 1.0,
            "force_towards_best_particle_state": 0.05,
            "final_force_towards_best_swarm_state": 0.10,
            "iterations_before_final_swarm_state_force_is_reached": 1500,
            "logging_and_videoframe_interval": 1,
            "number_of_rejections_to_converge": 500,
            "number_of_iterations_before_giving_up": 50000,
            "maximum_allowed_distance_between_molecules": 200.0
          }
        }
      },
      {
        "title": "local",
        "transforms": {
          "translation": {
            "scaling": 20.0
          },
          "rotation": {
            "scaling": 3.1415
          },
          "rotatable_bonds": {
            "scaling": 3.1415,
            "module": "custom.gags",
            "function": "get_rotatable_bonds"
          }
        },
        "search": {
          "module": "search.mc",
          "parameters": {
            "initial_temperature": 0.01,
            "temperature_change_factor_per_iteration": 0.99,
            "maximum_initial_random_step": 0.0,
            "number_of_rejections_to_converge": 1000,
            "number_of_iterations_before_giving_up": 100000,
            "maximum_allowed_distance_between_molecules": 200.0
          }
        }
      }
    ]

Rotatable bonds
~~~~~~~~~~~~~~~

The are two functions which can be used to select
:meth:`~murdock.transforms.ConfigDeclaration.rotatable_bonds()` in GAGs:

    - :func:`get_glycosidic_bonds()` (glycosidic linkages)
    - :func:`get_rotatable_bonds()` (all rotatable bonds)

Correct MOE files
~~~~~~~~~~~~~~~~~

The function :func:`correct_gag_residue_names_messed_up_by_moe()`, which fixes
some false GAG residue names introduced by MOE, can be used for
:meth:`~murdock.runner.docking.ConfigDeclaration.preprocessing()`.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import range

import logging
import traceback

if __name__ == 'murdock.custom.gags':
    import murdock.molstruct
    import murdock.misc


log = logging.getLogger('custom.gags')


GAG_RESIDUE_NAMES = (
    '01G', '02u', '02Y', '02Z', '03u', '03Z', '04B', '04V', '04Y', '05Y',
    '06B', '06L', '06V', '06Y', '07B', '07u', '07V', '07Y', '07Z', '08G',
    '09G', '09Y', '0GB', '0LB', '0uA', '0VB', '0YA', '0YB', '0ZB', '34B',
    '34V', '34Y', '36B', '36L', '36V', '36Y', '37B', '37V', '39Y', '3LB',
    '3VB', '3YA', '3YB', '41G', '42u', '42Y', '42Z', '43u', '43Z', '46V',
    '46Y', '47u', '47Y', '47Z', '48G', '49G', '4GA', '4uA', '4VB', '4YA',
    '4ZB')


def correct_gag_residue_names_messed_up_by_moe(molstruct):
    """Rename messed up GAG residue names from MOE files.

    1. Undo capitalization (e.g. `02U` --> `02u`).
    2. Remove leading `Q` (e.g. `Q42u` --> `42u`).

    """
    REP_TABLE = {'02U': '02u', '03U': '03u', '07U': '07u', '0UA': '0uA',
                 '42U': '42u', '47U': '47u', '4UA': '4uA'}
    for residue in molstruct.residues():
        if residue.name is not None and residue.name[0] == 'Q':
            residue.name = residue.name[1:]
        if residue.name is not None and residue.name in REP_TABLE:
            residue.name = REP_TABLE[residue.name]
    return True


def get_glycosidic_bonds(bonds, receptor=None):
    """Return a list of glycosidic bonds in a GAG.

    A definition of `glycosidic bond` can be found at:
    http://www.en.wikipedia.org/wiki/Glycosidic_bond

    The UPAC defninitions for the `glycosidic bond` and its torsional angles
    `phi` and `psi` can be found in: `Pure & Appl. Chem., Vol. 55, No. 8, pp.
    1269-1272, 1983`.

    Or as a free copy at: http://www.chem.qmul.ac.uk/iupac/misc/psac.html#220

    """
    glyc_bonds = []
    for bond in bonds:
        if bond in glyc_bonds:
            continue
        res0 = murdock.misc.get_source(
            bond.atoms[0], src_type=murdock.molstruct.Atom).residue
        res1 = murdock.misc.get_source(
            bond.atoms[1], src_type=murdock.molstruct.Atom).residue
        # filter bonds
        if res0.name not in GAG_RESIDUE_NAMES:
            continue
        if res1.name not in GAG_RESIDUE_NAMES:
            continue
        if res0.name == res1.name:
            continue
        # select bond
        if bond.atoms[0].element[0] == 'O':
            ox = bond.atoms[0]
            c = bond.atoms[1]
        elif bond.atoms[1].element[0] == 'O':
            ox = bond.atoms[1]
            c = bond.atoms[0]
        else:
            log.fatal(
                'Unexpected bond between atoms `%s` and `%s`. Two sugar '
                'monomers are not connected by an `O`. Only O-glycosidic '
                'bonds are supported so far.', bond.atoms[0].name,
                bond.atoms[1].name)
            return False
        x = int(ox.name[1])
        if c.name == 'C1':
            phi_bond = bond
            bs = [_b for _b in ox.bonds if _b is not bond]
            if len(bs) != 1:
                log.fatal(
                    'Unexpected number of bonds (%d) for atom `%s` '
                    '(expected 2).', len(bs), ox.name)
                return False
            psi_bond = bs[0]
            c1 = c
            cx = [_a for _a in psi_bond.atoms if _a is not ox][0]
        else:
            bs = [_b for _b in ox.bonds if _b is not bond]
            if len(bs) != 1:
                log.fatal(
                    'Unexpected number of bonds (%d) for atom `%s` (expected '
                    '2).', len(bs), ox.name)
                return False
            phi_bond = bs[0]
            psi_bond = bond
            cx = c
            c1s = [_a for _a in phi_bond.atoms if _a is not ox]
            if len(c1s) != 1:
                log.fatal(
                    'Unexpected bond between atoms `%s` and `%s`.',
                    bond.atoms[0].name, bond.atoms[1].name)
                return False
            c1 = c1s[0]
        if phi_bond in glyc_bonds and psi_bond in glyc_bonds:
            continue
        phi_bond.name = 'phi'
        psi_bond.name = 'psi'
        o5s = [_a for _a in c1.bonded if _a.name == 'O5']
        if len(o5s) != 1:
            log.fatal(
                'Unexpected bond between atoms %d (`%s`) and %d (`%s`).',
                bond.atoms[0].serial, bond.atoms[0].name, bond.atoms[1].serial,
                bond.atoms[1].name)
            return False
        o5 = o5s[0]
        cxme = [_a for _a in cx.bonded if _a.name == 'C%d' % (x - 1)][0]
        if phi_bond not in glyc_bonds:
            phi_bond.set_torsatoms([o5, c1, ox, cx])
            glyc_bonds.append(phi_bond)
        if psi_bond not in glyc_bonds:
            psi_bond.set_torsatoms([c1, ox, cx, cxme])
            glyc_bonds.append(psi_bond)
    return glyc_bonds


def get_rotatable_bonds(bonds, receptor=None):
    """Return a list of all rotatable bonds in a GAG.
    """
    ring = ('C1', 'C2', 'C3', 'C4', 'C5', 'O5')
    rotbonds = get_glycosidic_bonds(bonds)
    for bond in bonds:
        if bond in rotbonds:
            continue
        if bond.atoms[0].source_atom.residue.name not in GAG_RESIDUE_NAMES:
            continue
        if bond.atoms[0].source_atom.residue.name not in GAG_RESIDUE_NAMES:
            continue
        if bond.atoms[0].name in ring and bond.atoms[1].name in ring:
            continue
        if len(bond.atoms[0].bonds) == 1:
            continue
        if len(bond.atoms[1].bonds) == 1:
            continue
        bond.name = '-'.join(
            sorted([bond.atoms[0].name[0], bond.atoms[1].name[0]]))
        for atom3 in bond.atoms[0].bonded:
            if atom3 != bond.atoms[1]:
                break
        for atom4 in bond.atoms[1].bonded:
            if atom4 != bond.atoms[0]:
                break
        bond.set_torsatoms([atom3, bond.atoms[0], bond.atoms[1], atom4])
        rotbonds.append(bond)
    return rotbonds


class PyMOLVisualization(object):
    """This class contains a number visualization methods for PyMOL.

    The methods provided can be loaded at the end of a PyMOL script to change
    to a simplified representation of GAGs. By passing this module as the
    command-line argument ``--pymolscript``, one of the function is
    automatically used to modify pictures of docked structures created by
    Murdock. The function currently activated can be found at the bottom of
    this module.

    """

    def __init__(self):
        pass

    def draw_lines_and_plates_and_sulfates(self):
        for obj, color in self._iterate_objects_and_colors():
            cgo = [COLOR, color[0], color[1], color[2]]
            cgo.extend(self._get_c1_c4_sticks(obj, 0.2, color, order='C4'))
            if not cgo:
                continue
            cgo.extend(self._get_ring_plates(obj, 0.6, color))
            cgo.extend(self._get_sulfate_sticks(obj, 0.8, 0.2, color))
            if len(cgo) < 5:
                continue
            print('Load cgo object `%s`' % obj)
            cmd.load_cgo(cgo, obj, 1)
        cmd.zoom(complete=1, buffer=2)
        return True

    def draw_lines_and_sulfates(self):
        for obj, color in self._iterate_objects_and_colors():
            cgo = [COLOR, color[0], color[1], color[2]]
            cgo.extend(self._get_c1_c4_sticks(obj, 0.3, color, order=None))
            if not cgo:
                continue
            cgo.extend(self._get_sulfate_sticks(obj, 0.8, 0.2, color))
            if len(cgo) < 5:
                continue
            print('Load cgo object `%s`' % obj)
            cmd.load_cgo(cgo, obj, 1)
        cmd.zoom(complete=1, buffer=2)
        return True

    def draw_lines_carboxyls_sulfates(self):
        for obj, color in self._iterate_objects_and_colors():
            print('Load cgo object `%s`.' % obj)
            try:
                cgo = [COLOR, color[0], color[1], color[2]]
                cgo.extend(self._get_c1_c4_sticks(obj, 0.3, color, order=None))
                if not cgo:
                    continue
                cgo.extend(self._get_sulfate_sticks(obj, 0.8, 0.2, color))
                cgo.extend(self._get_carboxyl_sticks(obj, 0.4, 0.2, color))
                if len(cgo) < 5:
                    continue
            except:
                print(
                    'Error: Can not apply cgo representation to object `%s`: '
                    '%s' % (obj, traceback.format_exc().splitlines()[-1]))
            else:
                cmd.load_cgo(cgo, obj, 1)
        cmd.zoom(complete=1, buffer=2)
        return True

    def _get_c1_c4_sticks(self, obj, r, color, order=None):
        """Create a stick CGO object connecting C1 and C4 atoms.

        The order may be ``None`` which connects all atom pairs in iterating
        order.

        If the parameter ``order`` starts with `C1` (e.g. `C1`, `C1-C4`, ...)
        or `C4` only every other connection is drawn.

        """
        cgo = []
        atoms = cmd.get_model('%s and name C1+C4' % obj).atom
        for i in range(len(atoms) - 1):
            a1 = atoms[i]
            a2 = atoms[i+1]
            if order is None or order[:2] == a1.name:
                cgo.extend(self._get_stick(a1.coord, a2.coord, r, color))
        return cgo

    def _get_plate(self, c1, c3, c4, d, color):
        c1 = numpy.array(c1)
        c3 = numpy.array(c3)
        c4 = numpy.array(c4)
        m = (c1 + c4) / 2
        n = numpy.cross(c4 - c1, c3 - c1)
        n /= numpy.linalg.norm(n)
        x = m - 0.5 * d * n
        y = m + 0.5 * d * n
        r = numpy.linalg.norm((c4 - c1) / 2) * 1.4
        r1, g1, b1 = color
        r2, g2, b2 = color
        return [
            CYLINDER, x[0], x[1], x[2], y[0], y[1], y[2], r, r1, g1, b1, r2,
            g2, b2, 1.0, 1.0]

    def _get_ring_plates(self, obj, d, color):
        """Create a CGO plate through C1, C3 and C4 representing the ring.
        """
        cgo = []
        atoms = cmd.get_model('%s and name C1+C3+C4' % obj).atom
        for i in range(len(atoms) - 2):
            a1 = atoms[i]
            a2 = atoms[i+1]
            a3 = atoms[i+2]
            if a1.name == 'C1':
                cgo.extend(
                    self._get_plate(a1.coord, a2.coord, a3.coord, d, color))
        return cgo

    def _get_sphere(self, m, r):
        return [SPHERE, m[0], m[1], m[2], r]

    def _get_stick(self, x, y, r, color):
        r1, g1, b1 = color
        r2, g2, b2 = color
        cgo = [
            CYLINDER, x[0], x[1], x[2], y[0], y[1], y[2], r, r1, g1, b1,
            r2, g2, b2, 1.0, 1.0]
        cgo.extend(self._get_sphere(x, r))
        cgo.extend(self._get_sphere(y, r))
        return cgo

    def _get_carboxyl_sticks(self, obj, sphere_r, stick_r, color):
        """Create a ball-and-stick CGO representation of the carboxyl groups.
        """
        cgo = []
        o6as = cmd.get_model('%s and (name O6A)' % obj).atom
        o6bs = cmd.get_model('%s and (name O6B)' % obj).atom
        for o6a, o6b in zip(o6as, o6bs):
            o6a_coords = numpy.array(o6a.coord)
            o6b_coords = numpy.array(o6b.coord)
            carboxyl_coords = (o6a_coords + o6b_coords) / 2
            cgo.extend(self._get_sphere(carboxyl_coords, r=sphere_r))
            carbons = cmd.get_model('%s and (name C1+C4)' % obj).atom
            minval = None
            minm = None
            for i in range(0, len(carbons) - 1, 2):
                c1 = carbons[i]
                c2 = carbons[i+1]
                c1_coords = numpy.array(c1.coord)
                c2_coords = numpy.array(c2.coord)
                if o6a.resn != c1.resn or o6a.resn != c2.resn:
                    continue
                m = (c1_coords + c2_coords) / 2
                d = numpy.linalg.norm(m - carboxyl_coords)
                if minval is None or d < minval:
                    minval = d
                    minm = m
            cgo.extend(self._get_stick(minm, carboxyl_coords, stick_r, color))
        return cgo

    def _get_sulfate_sticks(self, obj, sphere_r, stick_r, color):
        """Create a ball-and-stick CGO representation of the sulfate groups.
        """
        cgo = []
        atoms = cmd.get_model('%s and (name S,S1,S2)' % obj).atom
        for atom in atoms:
            cgo.extend(self._get_sphere(atom.coord, r=sphere_r))
            acoords = numpy.array(atom.coord)
            carbons = cmd.get_model('%s and (name C1+C4)' % obj).atom
            minval = None
            minm = None
            for i in range(0, len(carbons) - 1, 2):
                c1 = carbons[i]
                c2 = carbons[i+1]
                c1coords = numpy.array(c1.coord)
                c2coords = numpy.array(c2.coord)
                if atom.resn != c1.resn or atom.resn != c2.resn:
                    continue
                m = (c1coords + c2coords) / 2
                d = numpy.linalg.norm(m - acoords)
                if minval is None or d < minval:
                    minval = d
                    minm = m
            cgo.extend(self._get_stick(minm, atom.coord, stick_r, color))
        return cgo

    def _iterate_objects_and_colors(self):
        for obj in cmd.get_object_list(selection='(*run*step* reflig*)'):
            color_index = cmd.get_object_color_index(obj)
            rgb = cmd.get_color_tuple(color_index)
            yield obj, rgb

if __name__ == 'pymol':
    import cmd
    from cgo import CYLINDER, SPHERE, COLOR
    import numpy
    p = PyMOLVisualization()
    p.draw_lines_carboxyls_sulfates()
