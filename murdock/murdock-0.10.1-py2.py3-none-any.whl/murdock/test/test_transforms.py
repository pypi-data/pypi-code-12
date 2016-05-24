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
A set of `py.test` routines for :mod:`murdock.transforms`.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import importlib
import logging
import numpy
import os
import pytest

from scipy.constants import pi

from murdock.math import Versor
import murdock.moldata
import murdock.logger
import murdock.runner.docking


murdock.logger.Logger(
    console_level=logging.WARNING, file_level=None)
log = logging.getLogger('test_transforms')

NDIGITS = 10

INPUTDIR = os.path.join(os.path.dirname(__file__), 'input')

LIGAND_FILEPATHS = (
    os.path.join(INPUTDIR, '1axm_ligand.mol2'),
    os.path.join(INPUTDIR, '1bfb_ligand.mol2'),
    os.path.join(INPUTDIR, '1ojm_ligand.mol2'))

RECEPTOR_FILEPATHS = (
    os.path.join(INPUTDIR, '1axm_receptor.mol2'),
    os.path.join(INPUTDIR, '1bfb_receptor.mol2'),
    os.path.join(INPUTDIR, '1ojm_receptor.mol2'))

AMOUNTS = (-10., -1., -0.1, -0.01, -0.001, 0., 0.001, 0.01, 0.1, 1., 10.)

T0 = [1.0, 1.0, 1.0]
TA = [1.0, 0.0, 0.0]
TB = [1.0, 1.0, 0.0]
TC = [1.0, 0.0, -1.0]
TD = [1.0, 1.0, 1.0]
TE = [1.0, 2.0, -1.0]

INOUT_TRANSLATION_UPDATE_VELOCITY = (
    ({'friction': 1.0}, [1.0, 1.0, 1.0]),
    ({'friction': 0.1}, [0.1, 0.1, 0.1]),
    ({'friction': 10.0}, [10.0, 10.0, 10.0]),
    ({'friction': 0.5, 'x1': (0.5, TA)}, [1.0, 0.5, 0.5]),
    ({'friction': 0.5, 'x1': (0.5, TB)}, [1.0, 1.0, 0.5]),
    ({'friction': 0.5, 'x1': (0.5, TC)}, [1.0, 0.5, 0.0]),
    ({'friction': 0.5, 'x1': (0.5, TD)}, [1.0, 1.0, 1.0]),
    ({'friction': 0.5, 'x1': (0.5, TE)}, [1.0, 1.5, 0.0]),
    ({'friction': 0.5, 'x1': (0.5, TA), 'x2': (0.5, TB)}, [1.5, 1.0, 0.5]),
    ({'friction': 0.5, 'x1': (0.5, TB), 'x2': (0.5, TC)}, [1.5, 1.0, 0.0]),
    ({'friction': 0.5, 'x1': (0.5, TC), 'x2': (0.5, TD)}, [1.5, 1.0, 0.5]),
    ({'friction': 0.5, 'x1': (0.5, TD), 'x2': (0.5, TE)}, [1.5, 2.0, 0.5]),
    ({'friction': 0.5, 'x1': (0.5, TE), 'x2': (0.5, TA)}, [1.5, 1.5, 0.0]))

AXES = ([1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0])

R0 = pi / 2
RA = 0.0
RB = pi / 2
RC = pi
RD = -pi / 2
RE = pi / 4

INOUT_ROTATION_UPDATE_VELOCITY = (
    ({'friction': 1.0}, pi / 2),
    ({'friction': 0.1}, pi / 20),
    ({'friction': 10.0}, pi),
    ({'friction': 0.5, 'x1': (0.5, RA)}, pi / 4),
    ({'friction': 0.5, 'x1': (0.5, RB)}, pi / 2),
    ({'friction': 0.5, 'x1': (0.5, RC)}, 3 * pi / 4),
    ({'friction': 0.5, 'x1': (0.5, RD)}, 0.0),
    ({'friction': 0.5, 'x1': (0.5, RE)}, 3 * pi / 8),
    ({'friction': 0.5, 'x1': (0.5, RA), 'x2': (0.5, RB)}, pi / 2),
    ({'friction': 0.5, 'x1': (0.5, RB), 'x2': (0.5, RC)}, pi),
    ({'friction': 0.5, 'x1': (0.5, RC), 'x2': (0.5, RD)}, pi / 2),
    ({'friction': 0.5, 'x1': (0.5, RD), 'x2': (0.5, RE)}, pi / 8),
    ({'friction': 0.5, 'x1': (0.5, RE), 'x2': (0.5, RA)}, 3 * pi / 8))


@pytest.fixture(scope='module', params=LIGAND_FILEPATHS)
def ligand_molstruct(request):
    lig = murdock.moldata.get_molstruct(filepath=request.param)
    assert lig
    assert lig.atoms
    return lig


@pytest.fixture(scope='module', params=RECEPTOR_FILEPATHS)
def receptor_molstruct(request):
    rec = murdock.moldata.get_molstruct(filepath=request.param)
    assert rec
    assert rec.atoms
    return rec


def molstruct_to_node(molstruct):
    node = murdock.tree.Node(
        name=molstruct.name, parent=None, object_serial=None)
    assert node.add_atoms(molstruct.atoms())
    assert len(molstruct.atoms()) == len(node.atoms)
    for bond in molstruct.bonds():
        node.add_bond(bond)
    assert len(molstruct.bonds()) == len(node.bonds)
    return node


def add_default_transforms_to_node(node):
    add_translation_to_node(node)
    add_rotation_to_node(node)
    add_bondrotation_to_node(node)


def add_translation_to_node(node):
    assert node.atoms
    assert node.set_as_dynamic()
    trans_tf = murdock.transforms.Translation(node=node, scaling=10.0)
    assert node.add_transformation(trans_tf)


def add_rotation_to_node(node):
    assert node.atoms
    assert node.set_as_dynamic()
    self_rot_tf = murdock.transforms.Rotation(node=node, scaling=pi)
    assert node.add_transformation(self_rot_tf)


def add_bondrotation_to_node(node):
    assert node.atoms
    select = [{'rotatable': True}]
    bonds = murdock.molstruct.get_bonds(
        node.bonds, receptor=False, select=select)
    assert node.init_rotbonds(bonds=bonds, scaling=pi)


TF_SETUPS = [
    add_translation_to_node, add_rotation_to_node,
    add_bondrotation_to_node, add_default_transforms_to_node]


class TestTransformation(object):
    """Tests for child classes of :class:`~murdock.transforms.Transformation`.
    """

    @pytest.mark.parametrize("tf_setup", TF_SETUPS)
    @pytest.mark.parametrize("amount", AMOUNTS)
    @pytest.mark.parametrize("random_speed", [True, False])
    def test_single_random_transformations(
            self, ligand_molstruct, tf_setup, amount, random_speed):
        lignode = molstruct_to_node(ligand_molstruct)
        tf_setup(lignode)
        transforms = [
            _tf for _n in lignode.iternodes() for _tf in _n.transforms]
        coords1 = [_x for _atom in lignode.atoms for _x in _atom.coords]
        steplen = abs(amount)
        for tf in transforms:
            state1 = tf.state()
            tf.randomize_velocity(amount, random_speed=random_speed)
            # assert: speed is not larger than steplength
            assert round(steplen - tf.speed(), NDIGITS) >= 0
            tf.step()
            # assert: distance is equal to speed
            assert round(tf.distance(state1) - tf.speed(), NDIGITS) == 0
            state2 = tf.state()
            tf.invert_velocity()
            # assert: speed is not larger than steplength
            assert round(steplen - tf.speed(), NDIGITS) >= 0
            tf.step()
            # assert: distance is equal to speed
            assert round(tf.distance(state2) - tf.speed(), NDIGITS) == 0
            # assert: initial state restored
            assert round(tf.distance(state1), NDIGITS) == 0
            coords2 = [_x for _atom in lignode.atoms for _x in _atom.coords]
            # assert: initial atom coordinates restored
            assert all([
                round(_c1 - _c2, NDIGITS) == 0 for _c1, _c2 in
                zip(coords1, coords2)])

    @pytest.mark.parametrize("tf_setup", TF_SETUPS)
    @pytest.mark.parametrize("amount", AMOUNTS)
    @pytest.mark.parametrize("random_speed", [True, False])
    def test_collective_random_transformations(
            self, ligand_molstruct, tf_setup, amount, random_speed):
        lignode = molstruct_to_node(ligand_molstruct)
        tf_setup(lignode)
        transforms = [
            _tf for _n in lignode.iternodes() for _tf in _n.transforms]
        states1 = [_tf.state() for _tf in transforms]
        coords1 = [_x for _atom in lignode.atoms for _x in _atom.coords]
        steplen = abs(amount)
        for tf in transforms:
            tf.randomize_velocity(amount, random_speed=random_speed)
            tf.step()
        for tf, state1 in zip(transforms, states1):
            # assert: speed is not larger than steplength
            assert round(steplen - tf.speed(), NDIGITS) >= 0
            # assert: distance is equal to speed
            assert round(tf.distance(state1) - tf.speed(), NDIGITS) == 0
        states2 = [_tf.state() for _tf in transforms]
        for tf in transforms:
            tf.invert_velocity()
        for tf in transforms[::-1]:
            tf.step()
        for tf, state1, state2 in zip(transforms, states1, states2):
            # assert: distance is equal to speed
            assert round(tf.distance(state2) - tf.speed(), NDIGITS) == 0
            # assert: initial state restored
            assert round(tf.distance(state1), NDIGITS) == 0
        coords2 = [_x for _atom in lignode.atoms for _x in _atom.coords]
        # assert: initial atom coordinates restored
        assert all([
            round(_c1 - _c2, NDIGITS) == 0 for _c1, _c2 in
            zip(coords1, coords2)])


class TestTranslation(object):
    """Tests for the :class:`~murdock.transforms.Translation` class.
    """

    @pytest.mark.parametrize("inout", INOUT_TRANSLATION_UPDATE_VELOCITY)
    def test_update_velocity(self, inout):
        anchor = murdock.molstruct.Atom(coords=numpy.array([0., 0., 0.]))
        node = murdock.tree.Node()
        node.add_atoms([anchor])
        tf = murdock.transforms.Translation(
            node=node, anchor=anchor, scaling=1.0)
        tf.velocity = numpy.array(T0)
        inp, out = inout
        tf.update_velocity(**inp)
        assert all(tf.velocity == out)


class TestRotation(object):
    """Tests for the :class:`~murdock.transforms.Rotation` class.
    """

    @pytest.mark.parametrize("axis", AXES)
    @pytest.mark.parametrize("inout", INOUT_ROTATION_UPDATE_VELOCITY)
    def test_update_velocity(self, axis, inout):
        anchor = murdock.molstruct.Atom(coords=numpy.array([0., 0., 0.]))
        node = murdock.tree.Node()
        node.add_atoms([anchor])
        tf = murdock.transforms.Rotation(
            node=node, anchor=anchor, scaling=1.0)
        tf.velocity = Versor(axis=axis, angle=R0)
        inp, out = inout
        kwargs = {'friction': inp['friction']}
        if 'x1' in inp:
            kwargs['x1'] = (
                inp['x1'][0], Versor(axis=axis, angle=inp['x1'][1]))
        if 'x2' in inp:
            kwargs['x2'] = (
                inp['x2'][0], Versor(axis=axis, angle=inp['x2'][1]))
        tf.update_velocity(**kwargs)
        assert round(tf.velocity.get_angle() - out, NDIGITS) == 0
        if out:
            assert all([
                round(_x1 - _x2, NDIGITS) == 0 for _x1, _x2 in
                zip(axis, tf.velocity.get_axis())])


class TestBondRotation(object):
    """Tests for the :class:`~murdock.transforms.BondRotation` class.
    """

    @pytest.mark.parametrize("inout", INOUT_ROTATION_UPDATE_VELOCITY)
    def test_update_velocity(self, ligand_molstruct, inout):
        lignode = molstruct_to_node(ligand_molstruct)
        select = [{'rotatable': True}]
        bonds = murdock.molstruct.get_bonds(
            lignode.bonds, receptor=False, select=select)
        for bond in bonds:
            bond.unbonded = bond
        lignode.init_rotbonds(bonds=bonds, scaling=1.0)
        for tf in lignode.descendant_transforms():
            tf.offset = -tf.bond.angle()
            tf.velocity = R0
            kwargs, out = inout
            tf.update_velocity(**kwargs)
            assert round(tf.velocity - out, NDIGITS) == 0
