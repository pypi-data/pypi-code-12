# -*- coding: utf-8 -*-
# Time-stamp: < contexttest.py (2016-01-20 09:04) >

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

import os.path
from unittest import TestCase

from summer import Context


class ContextTest(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_context_creation(self):
        ctx = Context(__file__, "custom.cfg")
        self.assertNotEqual(ctx, None)

        self.assertNotEqual(ctx.config, None)
        path = os.path.join(os.path.dirname(__file__), "custom.cfg")
        self.assertEqual(ctx.config.get("DEFAULT", "var1"), "var1")
        tmp = ctx.config.getboolean("CUSTOM_SECTION", "var2")
        self.assertEqual(tmp, True)

        self.assertNotEqual(ctx.summer_config, None)
        path = os.path.join(os.path.dirname(__file__), "summer.cfg")

        self.assertNotEqual(ctx.session_factory, None)
        self.assertNotEqual(ctx.session_factory.sessionmaker, None)
        self.assertNotEqual(ctx.session_factory.metadata, None)
