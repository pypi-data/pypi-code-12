# -*- coding: utf-8 -*-
# Time-stamp: < sftest.py (2016-01-20 09:04) >

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

from threading import Thread
from unittest import TestCase

from summer import Context
from summer import SessionFactory


class SessionFactoryTest(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_session_factory(self):
        ctx = Context(__file__, "custom.cfg")
        self.assertNotEqual(ctx, None)
        sf = ctx.session_factory
        self.assertNotEqual(sf, None)

        s1 = sf.get_sqlalchemy_session()
        s2 = sf.get_sqlalchemy_session()
        self.assertTrue(s1 == s2)

        class DaoTestThread(Thread):

            def __init__(self, sf: SessionFactory):
                Thread.__init__(self)
                self.sf = sf
                self.s3 = None

            def run(self):
                self.s3 = self.sf.get_sqlalchemy_session()

        thread = DaoTestThread(sf)
        thread.start()
        thread.join()
        s3 = thread.s3
        self.assertFalse(s1 == s3)
