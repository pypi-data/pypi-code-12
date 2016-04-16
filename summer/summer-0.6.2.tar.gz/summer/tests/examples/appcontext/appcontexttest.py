# -*- coding: utf-8 -*-
# Time-stamp: < appcontexttest.py (2016-02-01 08:45) >

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

"""Most simple standalone example.

Check the sample config files in this directory.  Look at the single
appcontext.py module.

"""

import logging
import logging.config
import os
import os.path

from unittest import TestCase

# configure logging as soon as possible
LOGGING_CFG = os.path.join(os.path.dirname(__file__), "logging.cfg")
logging.config.fileConfig(LOGGING_CFG)
logger = logging.getLogger(__name__)
logger.info("logging config = %s", LOGGING_CFG)

from .appcontext import ApplicationContext, Entity


class AppContextTest(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_appcontext(self):
        # provide custom config file
        ctx = ApplicationContext(__file__, "custom.cfg")

        # log some message
        logger.debug("so far, so good, so what")

        # obtain 1st business object -- our command line parser for application
        parser = ctx.option_parser
        # but there is nothing to parse, so lets just ignore it for now
        #(args, opts) = parser.parse_args(sys.argv[1:])

        # obtain manager object @transactional proxy
        mng = ctx.entity_manager_proxy
        # call business method -- note the transaction start and end in the log
        obj = Entity()
        mng.create_entity(obj)

        # another log message
        logger.debug("end of program")
