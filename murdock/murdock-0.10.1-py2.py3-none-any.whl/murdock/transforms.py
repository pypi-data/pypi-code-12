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
Module :mod:`murdock.transforms`
--------------------------------

A module to handle geometric transformations using the classes
:class:`Translation`, :class:`Rotation` and :class:`BondRotation`. Their common
API  is defined by the base class :class:`Transformation`.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import random

import numpy
import scipy.constants

import murdock.config
import murdock.math

log = logging.getLogger('transforms')


class TransformationError(Exception):
    pass


class Transformation(object):

    def __init__(
            self, node, max_step=None, name=None, scaling=None, offset=None,
            source=None):
        if name is None:
            name = self.__class__.__name__
        #: name of this transformation type (e.g. `translation`)
        self.name = name
        #: the :class:`~murdock.tree.Node` for which this
        #: :class:`~murdock.transforms.Transformation` is defined
        self.node = node
        #: normalization constant (not generically used in this module; may be
        #: used, e.g., in search modules)
        self.scaling = scaling
        #: current velocity
        self.velocity = None
        #: maximum step size allowed
        self.max_step = max_step
        #: list of state values (for sampling analysis)
        self.history = []
        #: history labels (e.g. [`x1`, `x2`, `x3`], or [`angle`])
        self.history_labels = []
        #: constant offset to the :meth:`~murdock.Transformation.state`
        #: (e.g. a reference angle or a change of coordinate systems)
        self.offset = offset
        #: reference to a source instance (set e.g. during a deepcopy)
        self.source = source

    def deepcopy(self, node, mappings=None, suffix=''):
        """Return a deepcopy of this instance.
        """
        raise NotImplementedError

    def distance(self, state):
        """Return the distance metric to another :meth:`state()`.
        """
        raise NotImplementedError

    def get_fmt_state(self):
        raise NotImplementedError

    def randomize_state(self, max_amount):
        """Perform a random :meth:`step`.
        """
        self.randomize_velocity(max_amount)
        self.step()

    def randomize_velocity(self, max_amount, random_speed=True, limit=False):
        raise NotImplementedError

    def speed(self):
        """Return a scalar based on the current :attr:`velocity`.
        """
        raise NotImplementedError

    def state(self):
        """Return current state.
        """
        raise NotImplementedError

    def step(self):
        raise NotImplementedError

    def update_velocity(self, friction, x1=None, x2=None):
        raise NotImplementedError


class Translation(Transformation):
    """A class describing translation in cartesian space.
    """

    def __init__(
            self, node, max_step=None, name=None, offset=None, scaling=None,
            source=None, anchor=None):
        super(Translation, self).__init__(
            node=node, max_step=max_step, name=name, offset=offset,
            scaling=scaling, source=source)
        #: atom instance defining the translational :meth:`state()`
        self.anchor = None
        if anchor is None:
            self.anchor = self.node.torsional_root()
        else:
            if anchor not in self.node.atoms:
                raise TransformationError(
                    'The `anchor` atom is not in the list of the `node` atoms '
                    'this transformation is working on.')
            self.anchor = anchor
        self.history_labels = ['x1', 'x2', 'x3']

    def deepcopy(self, node, mappings, suffix=''):
        """Return a deepcopy of this instance.
        """
        name = '%s%s' % (self.name, suffix)
        anchor = mappings[self.anchor]
        if anchor not in node.atoms:
            raise TransformationError(
                'The `anchor` atom is not in the list of the `node` atoms '
                'this transformation is working on.')
        if self.offset is None:
            offset = None
        else:
            offset = self.offset.copy()
        return self.__class__(
            node=node, max_step=self.max_step, name=name, offset=self.offset,
            scaling=self.scaling, source=self, anchor=anchor)

    def distance(self, state):
        return numpy.linalg.norm(self.state() - state)

    def get_fmt_state(self):
        return list(self.state())

    def invert_velocity(self):
        self.set_velocity(-self.velocity)

    def randomize_velocity(self, max_amount, random_speed=True, limit=False):
        if random_speed:
            amount = max_amount * random.random()**(1./3)
        else:
            amount = max_amount
        axis = murdock.math.random_unit_vector()
        self.set_velocity(amount * axis, limit=limit)
        return True

    def set_velocity(self, v, limit=True):
        if limit and self.max_step is not None:
            norm = numpy.linalg.norm(v)
            if norm > self.max_step:
                v = v / norm * self.max_step
        self.velocity = v

    def speed(self):
        return numpy.linalg.norm(self.velocity)

    def state(self):
        """Return the current state of this :class:`Transformation`.

        For a :class:`Translation`, the state equals the cartesian coordinates
        of the atom :attr:`Translation.anchor` in Anstroem
        (with added :attr:`~murdock.transforms.Transformation.offset`).

        """
        if self.offset is None:
            return self.anchor.coords.copy()
        else:
            return self.anchor.coords + self.offset

    def step(self):
        """Translate all atom coordinates.
        """
        for atom in self.node.atoms:
            atom.coords += self.velocity
        return True

    def update_velocity(self, friction, x1=None, x2=None):
        state = self.state()
        v = friction * self.velocity
        if x1 is not None:
            v += x1[0] * (x1[1] - state)
        if x2 is not None:
            v += x2[0] * (x2[1] - state)
        self.set_velocity(v)


class Rotation(Transformation):
    """A class describing a rigid rotation.
    """

    def __init__(
            self, node, max_step=None, name=None, offset=None, scaling=None,
            source=None, anchor=None, state=None):
        super(Rotation, self).__init__(
            node=node, max_step=max_step, name=name, offset=offset,
            scaling=scaling, source=source)
        #: atom instance defining the center of rotation
        self.anchor = None
        if anchor is not None:
            self.anchor = anchor
        else:
            self.anchor = self.node.torsional_root()
        if self.anchor not in self.node.atoms:
            raise TransformationError(
                'The `anchor` atom is not in the list of the `node` atoms '
                'this transformation is working on.')
        #: rotational velocity (:class:`~.math.Versor` instance)
        self.velocity = None
        #: rotational state (:class:`~.math.Versor` instance)
        if state is None:
            self._state = murdock.math.Versor()
        else:
            self._state = state.copy()
        self.history_labels = ['axis 1', 'axis 2', 'axis 3', 'angle']

    def deepcopy(self, node, mappings, suffix=''):
        """Return a deepcopy of this instance.
        """
        name = '%s%s' % (self.name, suffix)
        anchor = mappings[self.anchor]
        if anchor not in node.atoms:
            raise TransformationError(
                'The `anchor` atom is not in the list of the `node` atoms '
                'this transformation is working on.')
        if self.offset is None:
            offset = None
        else:
            offset = offset.copy()
        state = self._state.copy()
        return self.__class__(
            node=node, max_step=self.max_step, name=name, scaling=self.scaling,
            offset=offset, source=self, anchor=anchor, state=state)

    def distance(self, state):
        return (self.state() / state).get_angle()

    def get_fmt_state(self):
        s = self.state()
        return list(s.get_axis()) + [s.get_angle()]

    def invert_velocity(self):
        self.set_velocity(self.velocity.invert())

    def randomize_velocity(self, max_amount, random_speed=True, limit=False):
        max_angle = min(scipy.constants.pi, abs(max_amount))
        v = murdock.math.Versor()
        v.randomize(max_angle=max_angle, random_angle=random_speed)
        self.set_velocity(v, limit=limit)
        return True

    def set_velocity(self, v, limit=True):
        if (
                limit and self.max_step is not None and
                v.get_angle() > self.max_step):
            v.set_angle(self.max_step)
        self.velocity = v

    def speed(self):
        return self.velocity.get_angle()

    def state(self):
        # Note that quaternion multiplications are non-commutive.
        if self.offset is None:
            return self._state.copy()
        else:
            return self.offset * self._state

    def step(self):
        axis = self.velocity.get_axis()
        angle = self.velocity.get_angle()
        murdock.math.rotate_atoms(
            self.node.atoms, self.anchor.coords, axis, angle)
        self._state = self.velocity * self._state

    def update_velocity(self, friction, x1=None, x2=None):
        v = self.velocity**friction
        state = self.state()
        dv = None
        if x1 is not None and x2 is None:
            dv = (x1[1] / state)**x1[0]
        if x2 is not None and x1 is None:
            dv = (x2[1] / state)**x2[0]
        if x1 is not None and x2 is not None and x1[0] + x2[0] != 0.:
            q1 = (x1[1] / state)**x1[0]
            q2 = (x2[1] / state)**x2[0]
            q12 = q1 * q2
            q21 = q2 * q1
            dv = (q12 / q21)**0.5 * q21
        if dv is not None:
            v1 = dv * v
            v2 = v * dv
            v = (v1 / v2)**0.5 * v2
        self.set_velocity(v)


class BondRotation(Transformation):
    """A class describing rotation about a covalent bond.
    """

    def __init__(
            self, node, max_step=None, name=None, offset=None, scaling=None,
            source=None, bond=None):
        super(BondRotation, self).__init__(
            node=node, max_step=max_step, name=name, offset=offset,
            scaling=scaling, source=source)
        #: rotatable :class:`~murdock.molstruct.Bond` affected
        if not isinstance(bond, murdock.molstruct.Bond):
            raise TransformationError(
                'The argument `bond` must have the type `%s`, not `%s`.' % (
                    murdock.molstruct.Bond, type(bond)))
        self.bond = bond
        self.history_labels = ['angle']

    def deepcopy(self, node, mappings, suffix=''):
        """Return a deepcopy of this instance.
        """
        name = '%s%s' % (self.name, suffix)
        bond = mappings[self.bond]
        return self.__class__(
            node=node, max_step=self.max_step, name=name, scaling=self.scaling,
            offset=self.offset, source=self, bond=bond)

    def distance(self, state):
        return murdock.math.angle_diff(self.state() - state)

    def get_fmt_state(self):
        return [self.state()]

    def invert_velocity(self):
        self.set_velocity(-self.velocity)

    def randomize_velocity(self, max_amount, random_speed=True, limit=False):
        max_angle = min(scipy.constants.pi, abs(max_amount))
        if random_speed:
            angle = random.uniform(-max_angle, max_angle)
        else:
            angle = (1. if random.random() < 0.5 else -1.) * max_angle
        self.set_velocity(angle, limit=limit)

    def set_velocity(self, v, limit=True):
        if abs(v) > scipy.constants.pi:
            v = (1. if v > 0. else -1.) * scipy.constants.pi
        if limit and self.max_step is not None and abs(v) > self.max_step:
            v = (1. if v > 0. else -1.) * self.max_step
        self.velocity = v

    def speed(self):
        return abs(self.velocity)

    def state(self):
        if self.offset is None:
            return self.bond.angle()
        else:
            return self.bond.angle() + self.offset

    def step(self):
        murdock.math.rotate_atoms(
            self.node.atoms, self.bond.atoms[0].coords, self._axis(),
            self.velocity)

    def update_velocity(self, friction, x1=None, x2=None):
        state = self.state()
        v = friction * self.velocity
        if x1 is not None:
            v += x1[0] * (x1[1] - state)
        if x2 is not None:
            v += x2[0] * (x2[1] - state)
        self.set_velocity(v)

    def _axis(self):
        """Get the current bond vector.
        """
        if self.bond.tors_atoms[0] in self.node.atoms:
            return murdock.math.norm_diff_vector(
                self.bond.tors_atoms[2].coords,
                self.bond.tors_atoms[1].coords)[1]
        else:
            return murdock.math.norm_diff_vector(
                self.bond.tors_atoms[1].coords,
                self.bond.tors_atoms[2].coords)[1]


class ConfigDeclaration(murdock.config.ConfigDeclaration):

    def transforms(self):
        """Configuration options defining sampling transformations:

        Default options from
        :meth:`~murdock.config.ConfigDeclaration.get_default_options` are used.

            - "translation":
                sample ligand translation during the conformational search
                `(dtype=dict, required=False)`

            - "rotation":
                sample rigid ligand rotation during the conformational search
                `(dtype=dict, required=False)`

            - "rotatable_bonds":
                sample bond rotation in the ligand (and/or receptor) during
                the conformational search `(dtype=dict, required=False)`

        In Murdock, all transformations are treated very similarly during
        conformational searches. The `scaling` gives each type of
        transformation an own normalization, which can be used to tune the
        sampling step size for different types of transformation. This allows
        more efficient sampling of the conformational space defined by the
        different transformation types.

        Example: For a translation set the `scaling` to 10.0 (Angstroem), for a
        rotation to 3.1415 (radians). The conformational search will now sample
        a translational range of 10.0 Angstroem in about the same amount of
        time as it samples a full rotation.

        """
        Option = murdock.config.ConfigOption
        opt = self.get_default_options()
        opt.append(Option(name='translation', dtype=dict, required=False))
        opt.append(Option(name='rotation', dtype=dict, required=False))
        opt.append(Option(name='rotatable_bonds', dtype=dict, required=False))
        return opt

    def translation(self):
        """Refer to :meth:`~ConfigDeclaration.basic_tf`.
        """
        return self.basic_tf()

    def rotation(self):
        """Refer to :meth:`~ConfigDeclaration.basic_tf`.
        """
        return self.basic_tf()

    def basic_tf(self):
        """Configuration options used by all transformations.

        Default options from
        :meth:`~murdock.config.ConfigDeclaration.get_default_options` are used.

            - "scaling":
                a factor used to scale the sampling step length in some search
                algorithms; if not given, Murdock will choose as described in
                :meth:`~murdock.runner.docking.DockingStep.setup_transforms()`
                `(dtype=float, required=False)`

            - "max_step":
                maximum step length for this transformation
                `(dtype=float, required=False)`

        """
        Option = murdock.config.ConfigOption
        opt = self.get_default_options()
        opt.append(Option(
            name='scaling', dtype=Option.float_gt_zero, required=False,
            default=None, description=' a factor used to scale the sampling '
            'step length in some search algorithms'))
        opt.append(Option(
            name='max_step', dtype=Option.float_gt_zero,
            description='maximum step for any transformation of this degree '
            'of freedom', required=False))
        return opt

    def rotatable_bonds(self):
        """Configuration options for rotatable bonds:

            - "scaling":
                refer to
                :meth:`~ConfigDeclaration.basic_tf`

            - "module":
                module containing the Python function used to define rotatable
                bonds `(dtype=str, default=molstruct)`

            - "function":
                Python function used to define rotatable bonds `(dtype=str,
                default=get_bonds)`

            - "arguments":
                dictionary of keyword arguments passed to the function; if
                arguments are required depends on the function chosen
                `(dtype=dict, required=False, validate=True)`

        To define rotatable bonds, a list of all bonds found in the molecular
        input structures is passed to the function set here. The function must
        take a list of :class:`~murdock.molstruct.Bond` instances as first
        argument (and optionally additional arguments), somehow filter it for
        bonds that are supposed to be rotatable and return the filtered list.
        All bonds returned are set rotatable during the conformational search.

        If "module" and "function" are not given, the default function
        :meth:`molstruct.get_bonds()
        <murdock.molstruct.ConfigDeclaration.arguments>` is used.

        """
        Option = murdock.config.ConfigOption
        opt = self.basic_tf()
        opt.append(Option(
            name='module', dtype=Option.string, description='Murdock module '
            'containing the Python function used to filter rotatable bonds '
            'from all bonds found in input structures', default='molstruct'))
        opt.append(Option(
            name='function', dtype=Option.string, description='Python '
            'function used to filter rotatable bonds from all bonds found in '
            'input structures', default='get_bonds'))
        opt.append(Option(
            name='arguments', dtype=dict, description='dictionary of '
            'arguments passed to the function', default={}, validate=True,
            required=False))
        return opt
