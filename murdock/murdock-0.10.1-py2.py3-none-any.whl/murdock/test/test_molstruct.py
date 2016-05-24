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
A set of `py.test` routines for :mod:`murdock.molstruct`.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest

import murdock.molstruct


ATOMS = (
    murdock.molstruct.Atom(coords=(1.0, 1.0, 1.0)),
    murdock.molstruct.Atom(coords=(3.6, 3.6, 3.6)),
    murdock.molstruct.Atom(coords=(-1.0, -1.0, -1.0))
    )


@pytest.mark.parametrize(
    'test_input,expected', (
        (ATOMS, (1.2, 1.2, 1.2)),
        ((ATOMS[0], ATOMS[1]), (2.3, 2.3, 2.3)),
        ((ATOMS[1], ATOMS[2]), (1.3, 1.3, 1.3)),
        ((ATOMS[2], ATOMS[0]), (0, 0, 0)),
    ))
def test_get_center(test_input, expected):
    center = murdock.molstruct.get_center(test_input)
    assert all(center == expected)


@pytest.mark.parametrize(
    'test_input,expected', (
        (ATOMS, ATOMS[0]),
        ((ATOMS[0], ATOMS[1]), ATOMS[0]),
        ((ATOMS[1], ATOMS[2]), ATOMS[1]),
        ((ATOMS[2], ATOMS[0]), ATOMS[2]),
    ))
def test_get_center_atom(test_input, expected):
    center_atom = murdock.molstruct.get_center_atom(test_input)
    assert  center_atom == expected
