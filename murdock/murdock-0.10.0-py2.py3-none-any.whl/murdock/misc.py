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
Module :mod:`murdock.misc`
--------------------------

A collection of miscellaneous helper classes and functions.

This module provides a number of unrelated classes and functions used
throughout the Murdock package.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import codecs
import collections
import importlib
import json
import logging
import os
import re
import signal
import time

import numpy
import scipy.spatial

import murdock.math


log = logging.getLogger('misc')


class ResidueFormatter(object):
    """Class used to consistently convert between residue nomenclatures.

    The implemented nomenclatures are
        name: residue name, e.g. ARG
        serial: integer residue serial number, e.g. 125
        key: combined name and serial as residue identifier, e.g. ARG:125
        short: shorter version of key (without special characters), e.g. ARG125

    """

    RESIDUE_KEY_SEPARATOR = ':'

    def __init__(self):
        self.key = None
        self.name = None
        self.serial = None

    @property
    def short(self):
        return '%s%s' % (self.name, self.serial)

    @classmethod
    def from_residue(cls, res):
        formatter = cls()
        if res.name.endswith(str(res.serial)):
            name = res.name[:len(str(res.serial))]
        else:
            name = res.name
        formatter.key = '%s%s%d' % (
            name, cls.RESIDUE_KEY_SEPARATOR, res.serial)
        formatter.name = name
        formatter.serial = res.serial
        return formatter

    @classmethod
    def from_key(cls, key):
        formatter = cls()
        formatter.key = key
        formatter.name = key.split(cls.RESIDUE_KEY_SEPARATOR)[0]
        formatter.serial = int(key.split(cls.RESIDUE_KEY_SEPARATOR)[1])
        return formatter


def cleanup_filename(filename):
    """Remove forbidden characters from filenames (UNIX & Windows).

    The following characters in ``filename`` will be replaced by an underscore:
    `/`, `\`, `?`, `%`, `*`, `:`, `|`, `"`, `<`, `>`, ` `

    .. note:: Do not apply this to full paths because any slashes are replaced.

    Args:
        filename: The original string.

    Returns:
        The modified string.

    """
    return re.sub(r'[/\\\?\%\*\:|\"<> ]', '_', filename)


def cluster_structs_dbscan(
        structs, epsilon, minpoints, func=murdock.math.atoms_rmsd):
    """Perform a DBSCAN algorithm and return clustered structure groups.

    Args:
        structs (sequence): A sequence of
            :class:`~.molstruct.MolecularStructure`,
            :class:`~.molstruct.Model`, :class:`~.molstruct.Chain` or
            :class:`~.molstruct.Residue` instances.

        epsilon (float): DBSCAN parameter (maximum cluster member distance)

        minpoints (int): DBSCAN parameter (minimum number of cluster members)

        func (Optional[function]): func: function used to calculate the
            distance between two items from ``structs``. Defaults to
            :func:`~.math.atoms_rmsd`.

    Returns:
        list: A list of clusters (each a sub-list of ``structs``) sorted by
            number of members.

    """
    def _distmat(sts):
        n = len(sts)
        dists = []
        atoms = {_s: _s.atoms() for _s in sts}
        for i, st in enumerate(sts):
            for j in xrange(i+1, n):
                dists.append(func(atoms[st], atoms[sts[j]]))
        return scipy.spatial.distance.squareform(dists)
    dmat = numpy.asarray(_distmat(structs))
    indices = numpy.arange(dmat.shape[0])
    clusters = numpy.zeros(dmat.shape[0]).astype(int)
    visited = numpy.zeros(dmat.shape[0]).astype(bool)
    mask = (dmat > 0) & (dmat <= epsilon)
    clustered = [mask[_i].nonzero()[0] for _i in indices]
    nclustered = [len(_x) for _x in clustered]
    cluster_id = 0
    for i in indices:
        if visited[i]:
            continue
        visited[i] = True
        if nclustered[i] < minpoints:
            continue
        cluster_id += 1
        clusters[i] = cluster_id
        jindices = list(clustered[i])
        for j in jindices:
            if j not in clusters:
                clusters[j] = cluster_id
            if visited[j]:
                continue
            visited[j] = True
            if nclustered[j] < minpoints:
                continue
            jindices.extend(list(clustered[j]))
    cdict = {}
    for struct, cluster_id in zip(structs, clusters):
        if not cluster_id:
            continue
        if cluster_id not in cdict:
            cdict[cluster_id] = []
        cdict[cluster_id].append(struct)
    return sorted(cdict.values(), key=lambda _x: len(_x), reverse=True)


def get_python_module(mod_name):
    """Translate input strings into a python module.
    """
    return importlib.import_module('murdock.%s' % mod_name)


def get_python_function(mod, funct_name):
    """Translate input strings into a python function.
    """
    try:
        return getattr(mod, funct_name)
    except AttributeError:
        return False


def get_source(obj, depth=None, src_type=None):
    """Return the `source` attribute with certain properties.

    The first property is a given `depth` (see example).

    Example:
        - ``get_source(obj, depth=1)`` returns ``obj.source``
        - ``get_source(obj, depth=2)`` returns ``obj.source.source``
        - ``get_source(obj, depth=3)`` returns ``obj.source.source.source``

    The second property is a given type (see example). if `depth` is not given,
    the largest depth with matching type is used.

    Example:
        If an object ``atom`` has the following properties:
            - ``type(atom) == <class 'murdock.molstruct.Atom'>``
            - ``type(atom.source) == <class 'murdock.molstruct.Atom'>``
            - ``type(atom.source.source) ==``\
              ``<class 'murdock.moldata.pdb.PDBRecord'>``
        Then:
            ``get_source(obj=atom, src_type=type(atom))`` returns\
            ``atom.source``

    """
    if depth is None and src_type is None:
        raise TypeError(
            'Either `depth` or `src_type` must be given. Alternatively, use '
            '`misc.get_original_source()`.')
    if depth is not None:
        if depth == 0:
            if src_type is None or src_type == type(obj):
                return obj
            else:
                return False
        else:
            return get_source(obj.source, depth=depth-1, src_type=src_type)
    else:
        try:
            obj.source
        except AttributeError:
            if src_type is None or src_type == type(obj):
                return obj
            else:
                return None
        src = get_source(obj.source, depth=None, src_type=src_type)
        if src is None:
            if src_type is None or src_type == type(obj):
                return obj
            else:
                return None
        else:
            return src


def finitefloat(val):
    f = float(val)
    if not numpy.isfinite(f):
        raise ValueError
    return f


def float_ge_zero(val):
    f = finitefloat(val)
    if f < 0:
        raise ValueError
    return f


def float_gt_zero(val):
    f = float_ge_zero(val)
    if f == 0:
        raise ValueError
    return f


def float_le_zero(val):
    f = finitefloat(val)
    if f > 0:
        raise ValueError
    return f


def float_lt_zero(val):
    f = float_le_zero(val)
    if f == 0:
        raise ValueError
    return f


def fmtpath(filepath, reldir=None):
    if reldir is None:
        return os.path.basename(filepath)
    reldir = os.path.join(os.path.dirname(reldir), '..')
    return os.path.relpath(filepath, reldir)


def int_ge_zero(val):
    i = int(val)
    if i < 0 or float(val) != i:
        raise ValueError
    return i


def int_gt_zero(val):
    i = int_ge_zero(val)
    if i == 0:
        raise ValueError
    return i


def int_le_zero(val):
    i = int(val)
    if i > 0 or float(val) != i:
        raise ValueError
    return i


def int_lt_zero(val):
    i = int_le_zero(val)
    if i == 0:
        raise ValueError
    return i


def load_ordered_json(filepath):
    with codecs.open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    return json.JSONDecoder(
        object_pairs_hook=collections.OrderedDict).decode(content)


def original_source(obj, recursion_depth=0):
    """Return the original `source` of `obj`.

    Example:
        If `obj.source`, `obj.source.source` and `obj.source.source.source` are
        defined, `obj.source.source.source` is returned.

    """
    try:
        obj.source
    except AttributeError:
        return obj, recursion_depth
    return original_source(obj.source, recursion_depth=recursion_depth + 1)


def list_to_rgb(data, low, high):
    """Return an RGB color list given by the gradient from ``low`` to ``high``.

    Example::

        ``low=(0, 0, 0)``, ``high=(0, 1, .4)``, ``data=[0, 1, 2, 4]`` gives the
        RGB values
        ``[(0., 0., 0.), (0., .25, .1), (0., .5, .2), (0., 1., .4)]``

    """
    if (False in (0 <= _val <= 1 for _val in low) or
            False in (0 <= _val <= 1 for _val in high)):
        raise TypeError(
            'The arguments `low` and `high` must be valid RGB tuples with '
            'values in range 0 - 1 (not e.g. 0 - 255); given are low=%s, '
            'high=%s' % (str(low), str(high)))
    low = numpy.array(low)
    high = numpy.array(high)
    grad = high - low
    minval = min(data)
    maxval = max(data)
    if minval == maxval:
        return None
    return [
        tuple(low + murdock.math.normalize(_val, minval, maxval) * grad) for
        _val in data]
