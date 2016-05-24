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
Module :mod:`murdock.custom.frcmod`
-----------------------------------

This module handles FRCMOD files (Amber parameter file).

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import codecs
import collections
import logging
import os
import traceback


log = logging.getLogger('custom.frcmod')


class FileError(Exception):
    pass


class File(object):

    def __init__(self):
        self.vdw_radii = collections.OrderedDict()

    def parse(self, filepath):
        try:
            with codecs.open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except IOError:
            log.error(
                'File `%s` can not be read: %s', filepath,
                traceback.format_exc().splitlines()[-1])
            return False
        key = None
        for i, line in enumerate(content.splitlines()):
            line = line.strip()
            if not line:
                key = None
                continue
            if key is None:
                key = line
                continue
            if key == 'NONBON':
                fields = line.split()
                aname = fields[0]
                try:
                    aval = float(fields[1])
                except TypeError:
                    log.error(
                        'Error in file `%s`, line %d, field 2: Float '
                        'excpected (found `%s`), line is skipped.', filepath,
                        i + 1, fields[1])
                    continue
                if aname in self.vdw_radii:
                    log.warning(
                        'Van-der-Waals radius for atom type `%s` already '
                        'assigned (%.4f), new value (%.4f) found in file '
                        '`%s`, line %d is ignored.', aname,
                        self.vdw_radii[aname], aval, filepath, i + 1)
                    continue
                self.vdw_radii[aname] = aval
        return True


def uselib(molstruct, filepath):
    libfile = File()
    filepath = os.path.expandvars(os.path.expanduser(filepath))
    if not libfile.parse(filepath):
        return False
    atoms = molstruct.atoms()
    matched = 0
    for atom in atoms:
        try:
            atom.vdw_radius = libfile.vdw_radii[atom.name]
            matched += 1
        except KeyError:
            continue
    log.info(
        'Van-der-Waals radii from file `%s` assigned to %d / %d atoms.',
        filepath, matched, len(atoms))
    return True
