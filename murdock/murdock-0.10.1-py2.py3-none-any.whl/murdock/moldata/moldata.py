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
Module :mod:`murdock.moldata.moldata`
-------------------------------------

A basic API for the molecular structure file formatters.

The function :func:`get_molstruct()` uses the file extension to
import a backend module, calls the corresponding parser and converter and
returns a :class:`~murdock.molstruct.MolecularStructure`.

Example::

    import murdock.moldata
    molstruct1 = murdock.moldata.get_molstruct('1axm.pdb')
    molstruct2 = murdock.moldata.get_molstruct('2axm.mol2')

A list of implemented backends is given :mod:`here <murdock.moldata>`.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import importlib
import logging
import os
import pkgutil


import murdock


log = logging.getLogger('moldata')


def convert_to_file(molstruct, ext, **kwargs):
    module = get_backend_module(ext)
    if module is None:
        return False
    f = module.File()
    f.from_molstruct(molstruct, **kwargs)
    return f


def get_backend_module(ext):
    ext = ext.lstrip('.')
    try:
        return importlib.import_module('murdock.moldata.%s' % ext)
    except ImportError:
        log.error('Murdock does not support the file extension `%s`.', ext)
        return None


def get_molstruct(filepath, infolog=True):
    """Parse `filepath` and return a :class:`~murdock.MolecularStructure`.
    """
    if not os.path.isfile(filepath):
        log.fatal('Can not open input file `%s`. File not found.', filepath)
        return False
    ext = _get_extension(filepath)
    module = get_backend_module(ext)
    if module is None:
        return False
    f = module.File(filepath=filepath)
    f.parse()
    m = f.to_molstruct()
    if not m:
        log.fatal(
            'File `%s` has critical errors and could not be converted into a '
            'molecular structure.', filepath)
        return False
    if infolog:
        log.info(
            'Found %d models, %d chains, %d residues, %d atoms and %d bonds.',
            len(m.models), len(m.chains()), len(m.residues()), len(m.atoms()),
            len(m.bonds()))
    return m


def known_extensions():
    return [
        '.%s' % _x[1].split('.')[-1] for _x in
        pkgutil.iter_modules(murdock.moldata.__path__, 'moldata.') if
        _x[1] != 'moldata.moldata']


def _get_extension(filepath):
    return os.path.splitext(filepath)[1]
