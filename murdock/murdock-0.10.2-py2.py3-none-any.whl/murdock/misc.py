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
from builtins import range

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


log = logging.getLogger(__name__)


class ResidueFormatter(object):
    """Class used to consistently convert between residue nomenclatures.

    Implemented nomenclatures:
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

    The following characters will be replaced by an underscore: ``/``, ``\``,
    ``?``, ``%``, ``*``, ``:``, ``|``, ``"``, ``<``, ``>``, `` ``.

    .. note:: Do not apply this to full paths because any slashes are replaced.

    Args:
        filename (str): The original string.

    Returns:
        str: The modified string.

    """
    return re.sub(r'[/\\\?\%\*\:|\"<> ]', '_', filename)


def cluster_structs_dbscan(
        structs, epsilon, minpoints, func=murdock.math.atoms_rmsd):
    """Perform a DBSCAN algorithm and return clustered structure groups.

    Args:
        structs (Sequence[...]): A sequence of
            :class:`~.molstruct.MolecularStructure`,
            :class:`~.molstruct.Model`, :class:`~.molstruct.Chain` or
            :class:`~.molstruct.Residue` instances.
        epsilon (float): DBSCAN parameter (maximum cluster member distance)
        minpoints (int): DBSCAN parameter (minimum number of cluster members)
        func (Optional[Callable[..., float]]): function used to calculate the
            distance between two items from ``structs``. Defaults to
            :func:`~.math.atoms_rmsd`.

    Returns:
        List[List[...], ...]: A list of clusters (each a sub-list of
            ``structs``) sorted by number of members.

    """
    def _distmat(sts):
        n = len(sts)
        dists = []
        atoms = {_s: _s.atoms() for _s in sts}
        for i, st in enumerate(sts):
            for j in range(i+1, n):
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


def finitefloat(val):
    """Convert argument into a finite float if possible.

    Raises a ValueError if the argument is a irregular float, e.g. numpy.inf.

    Args:
        val (float, int): Value to be converted.

    Returns:
        float: Converted value.

    Raises:
        ValueError: If argument is can not be converted into a finite float.

    Examples:
        Consider a regular finite float:

        >>> x = 1.337

        Conversion by calling float():

        >>> float(x)
        1.337

        Conversion by calling finitefloat():

        >>> finitefloat(x)
        1.337

        Now consider an infinite float:

        >>> from numpy import inf

        Conversion by calling float():

        >>> float(inf)
        inf

        Conversion by calling finitefloat():

        >>> finitefloat(inf)
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
          File "/usr/local/lib/python2.7/dist-packages/murdock/misc.py", line \
          187, in finitefloat
            raise ValueError
        ValueError

    """
    f = float(val)
    if not numpy.isfinite(f):
        raise ValueError
    return f


def get_python_module(mod_name):
    """Return Murdock module given its name.

    Simple wrapper for :func:`importlib.import_module()`, adding the package
    name `murdock` to the argument string.

    Args:
        mod_name (str): Murdock module name.

    Returns:
        module: Murdock module.

    Raises:
        ImportError: If the Murdock module can not be imported.

    """
    return importlib.import_module('murdock.%s' % mod_name)


def get_python_function(mod, func_name):
    """Return Python function given its module and name.

    Args:
        mod (module): Python module.
        func_name (str): Python function name.

    Returns:
        Callable: Python function.

    Raises:
        AttributeError: If the module does not contain the function.

    """
    try:
        return getattr(mod, func_name)
    except AttributeError:
        return False


def get_source(obj, depth=None, src_type=None):
    """Return the ``source`` attribute with certain properties.

    This function walks through a series of objects linked by ``source``
    attributes. If ``src_type`` is given, the first object matching the type
    is returned.

    .. seealso:: :func:`original_source()`

    Args:
        obj (Any): Any object with ``source`` attribute.
        depth (int): Recursion depth to retrieve source object.
        src_type (type): Source object type.

    Returns:
        Any: Source object.

    Examples:
        Consider the following chain of objects.

        >>> f = murdock.moldata.mol2.File()
        >>> mol = f.to_molstruct()
        >>> node = murdock.tree.Node(name=mol.name, source=mol)
        >>> node_copy = node.deepcopy()

        They are connected by their ``source`` attributes.

        >>> mol.source is f
        True
        >>> node.source is mol
        True
        >>> node_copy.source is node
        True

        To retrieve objects up the chain one may use the ``depth`` argument.

        >>> node is get_source(node_copy, depth=1)
        True
        >>> mol is get_source(node_copy, depth=2)
        True
        >>> f is get_source(node_copy, depth=3)

        After objects have been copied multiple times, it may become more
        practical to use the ``src_type`` argument to retrieve a certain
        source type up the chain.

        >>> node is get_source(node_copy, src_type=murdock.tree.Node)
        True
        >>> mol is get_source(\
            node_copy, src_type=murdock.molstruct.MolecularStructure)
        True
        >>> f is get_source(node_copy, src_type=murdock.moldata.mol2.File)
        True

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


def fmtpath(filepath, reldir=None):
    """Format filepath to a short (but still descriptive) relative path.

    Args:
        filepath (str): Full filepath.

    Returns:
        str: Shorter filepath.

    """
    if reldir is None:
        return os.path.basename(filepath)
    reldir = os.path.join(os.path.dirname(reldir), '..')
    return os.path.relpath(filepath, reldir)


def load_ordered_json(filepath):
    """Read JSON file into an :class:`~collections.OrderedDict` instance.

    Args:
        filepath (str): Filepath to JSON file.

    Returns:
        Dict[...]: :class:`~collections.OrderedDict` instance.

    Raises:
        IOError: If file can not be opened.
        ValueError: If file is not a valid JSON file.

    """
    with codecs.open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    return json.JSONDecoder(
        object_pairs_hook=collections.OrderedDict).decode(content)


def original_source(obj, recursion_depth=0):
    """Return the original ``source`` of `obj`.

    .. seealso:: :func:`get_source()`

    Args:
        obj (Any): Any object with ``source`` attribute.

    Returns:
        Any: Source object.

    Examples:
        Consider the following chain of objects.

        >>> f = murdock.moldata.mol2.File()
        >>> mol = f.to_molstruct()
        >>> node = murdock.tree.Node(name=mol.name, source=mol)
        >>> node_copy = node.deepcopy()

        They are connected by their ``source`` attributes.

        >>> mol.source is f
        True
        >>> node.source is mol
        True
        >>> node_copy.source is node
        True

        Use this function to retrieve the object with ``source`` attribute
        which is highest up the chain.

        >>> f is original_source(node_copy)
        True
        >>> f is original_source(node)
        True
        >>> f is original_source(mol)
        True

    """
    try:
        obj.source
    except AttributeError:
        return obj, recursion_depth
    return original_source(obj.source, recursion_depth=recursion_depth + 1)


def list_to_rgb(data, low, high):
    """Return an RGB color list given by the gradient from ``low`` to ``high``.

    The arguments ``low`` and ``high`` must be valid RGB tuples with values
    between 0 and 1 (not 0 to 255).

    Args:
        data (Iterable[float, ...]): Data to be encoded as RGB.
        low (Tuple[float, float, float]): Lower limit.
        high (Tuple[float, float, float]): Upper limit.

    Examples:
        >>> list_to_rgb(low=(0, 0, 0), high=(0, 1, .4), data=[0, 1, 2, 4])
        [(0.0, 0.0, 0.0), (0.0, .25, 0.1), (0.0, 0.5, 0.2), (0.0, 1.0, 0.4)]

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
