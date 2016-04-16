# -*- coding: utf-8 -*-
# Time-stamp: < __init__.py (2016-01-24 01:25) >

# Copyright (C) 2009-2016 Martin Slouf <martin.slouf@sourceforge.net>
#
# This file is a part of Summer.
#
# Summer is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import logging.config
import os.path

LOGGING_CFG = os.path.join(os.path.dirname(__file__), "logging.cfg")
logging.config.fileConfig(LOGGING_CFG)

from summer.tests.contexttest import *
from summer.tests.daotest import *
from summer.tests.domaintest import *
from summer.tests.sftest import *
from summer.tests.stringutilstest import *
from summer.tests.pctest import *
from summer.tests.pcgtest import *

from summer.tests.examples import *
