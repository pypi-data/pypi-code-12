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
Module :mod:`murdock.math`
--------------------------

Provides a number of math-related classes and functions used througout the
Murdock package.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import random

import numpy
from scipy.constants import pi
import scipy.spatial

log = logging.getLogger('math')


class Versor(object):
    """Class representing a versor, i.e. a unit quaternion.

    Versors are unit quaternions used as an algebraic parametrization of
    rotations. Refer to the `article on Wikipedia
    <https://en.wikipedia.org/wiki/Versor>` for details.

    """

    def __init__(self, q=None, axis=None, angle=None):
        #: quaternion 4-vector
        self.q = numpy.array([0., 0., 0., 1.])
        if (
                (q is not None and (axis is not None or angle is not None)) or
                (q is None and (axis is None != angle is None))):
            raise ValueError(
                'A Versor must be initialized either by giving a '
                'quaternion vector `q` or by giving an `axis` and `angle` '
                'from which a quaternion vector `q` can be calculated.')
        if q is not None:
            self._set_q(q)
        elif axis is not None:
            if axis == 'random':
                axis = random_unit_vector()
            self._set_axis_angle(axis, angle)

    def copy(self):
        return Versor(self.q.copy())

    def get_angle(self):
        return 2. * numsave_arccos(self.q[3])

    def get_axis(self):
        norm = numpy.linalg.norm(self.q[:3])
        if not norm:
            return numpy.array([1., 0., 0.])
        return self.q[:3] / norm

    def set_angle(self, angle):
        axis = self.get_axis()
        self._set_axis_angle(axis, angle)

    def invert(self):
        return Versor([self.q[0], self.q[1], self.q[2], -self.q[3]])

    def randomize(self, max_angle=None, random_angle=True):
        """Randomize quaternion.

        For angles ``max_angle >= pi / 36``, use Shoemake`s method. For smaller
        angles, use a small angle approximation.

        """
        if max_angle == 0:
            return True
        if max_angle is not None and not (0 <= max_angle <= pi):
            raise ValueError(
                'Quaternion must be randomized with max_angle=None or '
                '0<=max_angle<=pi (given max_angle=%fpi).' %
                (max_angle / pi))
            max_angle = min(max_angle, pi)
        if max_angle is None and random_angle is None:
            raise ValueError(
                'If parameter `random_angle` is False, `max_angle` must be '
                'given.')
        if not random_angle:
            # Use method of Cook / Marsaglia.
            self._set_axis_angle(random_unit_vector(), max_angle)
        elif max_angle is not None and max_angle < pi / 36.:
            # Use small angle approximation.
            while True:
                s = max_angle**3 * random.random()
                a = s**(1. / 3)
                if random.random() < numpy.sin(a)**2 / a**2:
                    self._set_axis_angle(random_unit_vector(), a)
                    break
        else:
            # Use Shoemake's method.
            while True:
                s = random.random()
                x1 = numpy.sqrt(1 - s)
                x2 = numpy.sqrt(s)
                t1 = 2 * pi * random.random()
                t2 = 2 * pi * random.random()
                self.q = numpy.array([
                    numpy.sin(t1) * x1, numpy.cos(t1) * x1, numpy.sin(t2) * x2,
                    numpy.cos(t2) * x2])
                if max_angle is None or self.get_angle() <= max_angle:
                    break
        return True

    def _set_axis_angle(self, axis, angle):
        axis /= numpy.linalg.norm(axis)
        self._set_q(
            [_x * numpy.sin(angle / 2.) for _x in axis] +
            [numpy.cos(angle / 2.)])

    def _set_q(self, q):
        self.q = numpy.array(q)
        self.q /= numpy.linalg.norm(self.q)
        if self.q[3] < 0:
            self.q = -self.q

    def __mul__(self, v):
        q1 = self.q
        q2 = v.q
        return Versor(numpy.array([
            q1[3] * q2[0] - q1[2] * q2[1] + q1[1] * q2[2] + q1[0] * q2[3],
            q1[2] * q2[0] + q1[3] * q2[1] - q1[0] * q2[2] + q1[1] * q2[3],
            -q1[1] * q2[0] + q1[0] * q2[1] + q1[3] * q2[2] + q1[2] * q2[3],
            -q1[0] * q2[0] - q1[1] * q2[1] - q1[2] * q2[2] + q1[3] * q2[3]]))

    def __truediv__(self, v):
        return self * v.invert()

    def __pow__(self, x):
        norm = numpy.linalg.norm(self.q[:3])
        if not norm:
            return Versor()
        n = self.q[:3] / norm
        angle = x * numsave_arccos(self.q[3])
        re = numpy.array([numpy.cos(angle)])
        im = n * numpy.sin(angle)
        return Versor(numpy.concatenate((im, re)))


def angle_diff(d):
    diff = d % (2 * pi)
    if diff <= pi:
        return diff
    return 2 * pi - diff


def atoms_rmsd(atoms1, atoms2):
    """Return the RMSD between two atom sequences.

    The RMSD is calculated over pairwise atom coordinates, i.e. atoms from
    ``atoms1`` and ``atoms2`` are matched based on their sequence index. Hence,
    the sequences ``atoms1`` and ``atoms2`` must have the same lengths.

    Args:
        atoms1: A sequence of :class:`~.molstruct.Atom` instances.
        atoms2: Another sequence of :class:`~.molstruct.Atom` instances.

    Returns:
        The float pair-wise RMSD (root mean square distance) between
        ``atoms1`` and ``atoms2``.

    Raises:
        ValueError: The two atom sequences have different lengths.

    """
    if not len(atoms1) == len(atoms2):
        raise ValueError(
            'Atom sequences have different lengths (atoms1 -> %d, atoms2 -> '
            '%d).' % (len(atoms1), len(atoms2)))
    msd = 0
    for atom1, atom2 in zip(atoms1, atoms2):
        msd += numpy.sum((atom1.coords - atom2.coords)**2)
    return numpy.sqrt(msd / len(atoms1))


def atoms_rmsatd(atoms1, atoms2):
    """Return the RMSATD between two atom sequences.

    The RMSATD is defined analogous to the RMSD (see :func:`.atoms_rmsatd`) but
    atoms from ``atoms1`` and ``atoms2`` are matched as the closest atoms of
    the same element (NOT by their sequence index). Hence, the sequences
    ``atoms1`` and ``atoms2`` must NOT have the same lengths.

    Args:
        atoms1: A sequence of :class:`~.molstruct.Atom` instances.
        atoms2: Another sequence of :class:`~.molstruct.Atom` instances.

    Returns:
        The float pair-wise RMSATD (root mean square atom type distance)
        between ``atoms1`` and ``atoms2``.

    """
    msd = 0
    for atom1 in atoms1:
        minsdist = None
        for atom2 in atoms2:
            if atom1.element != atom2.element:
                continue
            sdist = numpy.sum((atom1.coords - atom2.coords)**2)
            if minsdist is None or sdist < minsdist:
                minsdist = sdist
        msd += minsdist
    return numpy.sqrt(msd / len(atoms1))


def distmat(atoms1, atoms2):
    """Return the euclidean distance matrix between two atom sequences.

    Args:
        atoms1: A sequence of :class:`~.molstruct.Atom` instances.
        atoms2: Another sequence of :class:`~.molstruct.Atom` instances.

    Returns:
        Euclidean distance matrix as numpy.ndarray.

    """
    return scipy.spatial.distance.cdist(
        numpy.array([_atom.coords for _atom in atoms1]),
        numpy.array([_atom.coords for _atom in atoms2]))


def norm_crossp(vec1, vec2):
    """Return the normalized cross product `vec1` x `vec2` and the norm.
    """
    vec = numpy.cross(vec1, vec2)
    norm = numpy.linalg.norm(vec)
    if norm == 0:
        return 0, numpy.array([0 for _ in vec])
    return norm, vec / norm


def norm_diff_vector(coords1, coords2):
    """Return the normalized difference vector between `coords1` and `coords2`.
    """
    vec = coords1 - coords2
    norm = numpy.linalg.norm(vec)
    if norm == 0:
        return 0, numpy.array([0 for _ in vec])
    return norm, vec / norm


def normalize(value, minval, maxval, invert=False):
    try:
        normalized = min(1., max(0, float(value - minval) / (maxval - minval)))
    except (FloatingPointError, ZeroDivisionError):
        normalized = 0.5
    if invert:
        return 1. - normalized
    else:
        return normalized


def numsave_arccos(arg):
    """Prevent math domain error in `numpy.arccos`.

    In numerical calculations the argument of a arccos might happen to be
    slightly out of its domain. Deviations of the argument up to 0.01 are
    caught and corrected here.

    """
    if 1 < arg < 1.001:
        return 0
    if -1.001 < arg < -1:
        return pi
    return numpy.arccos(arg)


def random_unit_vector():
    """Return random unit vector from an equal distribution on a sphere.

    References: Cook 1957, Marsaglia 1972

    """
    while True:
        x0 = 2 * random.random() - 1
        x1 = 2 * random.random() - 1
        x2 = 2 * random.random() - 1
        x3 = 2 * random.random() - 1
        r = x0**2 + x1**2 + x2**2 + x3**2
        if r < 1:
            break
    return (numpy.array([(x1 * x3 + x0 * x2) * 2,
                         (x2 * x3 - x0 * x1) * 2,
                         (x0**2 + x3**2 - x1**2 - x2**2)]) / r)


def rotate_atoms(atoms, anchor, axis, phi):
    """Rotate `coords` in cartesian space.

    The cartesian coordinates `coords` are rotated about the axis through the
    point `anchor` with direction `axis` (unit vector) by the angle `phi`. The
    parameters `coords`, `anchor` and `axis` must be given as numpy arrays
    [x, y, z], `phi` must be given in radians.

    """
    sin_phi = numpy.sin(phi)
    cos_phi = numpy.cos(phi)
    emcp = 1 - cos_phi
    const1 = anchor[0] * (axis[1]**2 + axis[2]**2)
    const2 = anchor[1] * axis[1] + anchor[2] * axis[2]
    const3 = - anchor[2] * axis[1] + anchor[1] * axis[2]
    const4 = anchor[1] * (axis[0]**2 + axis[2]**2)
    const5 = anchor[0] * axis[0] + anchor[2] * axis[2]
    const6 = anchor[2] * axis[0] - anchor[0] * axis[2]
    const7 = anchor[2] * (axis[0]**2 + axis[1]**2)
    const8 = anchor[0] * axis[0] + anchor[1] * axis[1]
    const9 = - anchor[1] * axis[0] + anchor[0] * axis[1]
    rotmat = numpy.matrix(
        [[emcp * axis[0] * axis[0] + cos_phi,
          emcp * axis[0] * axis[1] - sin_phi * axis[2],
          emcp * axis[0] * axis[2] + sin_phi * axis[1],
          emcp * (const1 - axis[0] * const2) + sin_phi * const3],
         [emcp * axis[1] * axis[0] + sin_phi * axis[2],
          emcp * axis[1] * axis[1] + cos_phi,
          emcp * axis[1] * axis[2] - sin_phi * axis[0],
          emcp * (const4 - axis[1] * const5) + sin_phi * const6],
         [emcp * axis[2] * axis[0] - sin_phi * axis[1],
          emcp * axis[2] * axis[1] + sin_phi * axis[0],
          emcp * axis[2] * axis[2] + cos_phi,
          emcp * (const7 - axis[2] * const8) + sin_phi * const9]])
    for atom in atoms:
        coords = numpy.append(atom.coords, [1])
        atom.coords = numpy.array(numpy.dot(rotmat, coords)).reshape(3)
    return True


def torsional_angle(v1, v2, v3, v4):
    """Calculate the torsional angle between the vectors `v1` to `v4`.

    All vectors are Numpy arrays. The torsional angle is defined as the angle
    between the planes v1-v2-v3 and v2-v3-v4.

    """
    # axis
    a23 = v3 - v2
    # direction
    c = numpy.cross(v1 - v2, a23)
    x = numpy.dot(v4 - v3, c)
    # angle
    n1 = numpy.cross(v2 - v1, a23)
    n2 = numpy.cross(a23, v4 - v3)
    e1 = n1 / numpy.linalg.norm(n1)
    e2 = n2 / numpy.linalg.norm(n2)
    angle = numsave_arccos(numpy.dot(e1, e2))
    if x >= 0:
        return angle
    return -angle
