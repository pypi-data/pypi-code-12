# -*- coding: utf-8 -*-
# Time-stamp: < daotest.py (2016-02-29 06:27) >

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
from summer import Entity
from summer import SessionFactory


class FooEntity(Entity):

    def __init__(self, foo):
        self.foo = foo


class DaoTest(TestCase):

    def setUp(self):
        self.ctx = Context(__file__, "custom.cfg")

    def tearDown(self):
        pass

    def test_session_factory(self):
        self.assertNotEqual(self.ctx, None)
        sf = self.ctx.session_factory
        self.assertNotEqual(sf, None)

        s1 = sf.get_sqlalchemy_session()
        s2 = sf.get_sqlalchemy_session()
        self.assertTrue(s1 == s2)

        class DaoTestThread(Thread):

            def __init__(self, sf):
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

    def test_connection(self):
        sf = self.ctx.session_factory
        self.assertNotEqual(sf, None)
        assert isinstance(sf, SessionFactory)

        query = "CREATE TABLE person (name TEXT, age INT)"
        dbcon = sf.get_connection().connection
        cursor = dbcon.cursor()
        cursor.execute(query)

        query = "INSERT INTO person (name, age) VALUES (?, ?)"
        for i in range(1, 9):
            tmp = {"name": "name_%d" % i, "age": i}
            cursor.execute(query, (tmp["name"], tmp["age"]))
        dbcon.commit()

        query = "SELECT * FROM person"
        cursor.execute(query)
        idx = 1
        row = cursor.fetchone()
        while row:
            self.assertEqual(row[0], "name_%d" % idx)
            self.assertEqual(row[1], idx)
            idx += 1
            row = cursor.fetchone()
        dbcon.commit()
