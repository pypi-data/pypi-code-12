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
Module :mod:`murdock.scoring`
-----------------------------

This module contains the base module :mod:`murdock.scoring.scoring`, which
specifies the Murdock scoring API, the base module
:mod:`~murdock.scoring.pool`, which provides a number of generic scoring terms
and a number of implemented scoring modules:

:mod:`murdock.scoring.custom`
    Allows to combine arbitrary scoring terms from the
    :mod:`~murdock.scoring.pool`.

:mod:`murdock.scoring.rmsd`
    Scores structures based on the RMSD to a reference.

:copyright: Copyright 2016 Malte Lichtner
:license: Apache 2.0, see LICENSE for details.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .scoring import *
