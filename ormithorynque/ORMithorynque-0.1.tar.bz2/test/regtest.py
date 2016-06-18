# -*- coding: utf-8 -*-
# ORMithorynque
# Copyright (C) 2016 Jean-Baptiste LAMY

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest, os, tempfile, datetime, weakref

import ormithorynque

class ormithorynqueTest(unittest.TestCase):
  def test_table_creation_1(self):
    database = ormithorynque.Database(":memory:")
    class Person(database.Object):
      nom = database.SQLAttribute(str)
    assert database.check_existing_table("Person") == ["nom"]
    
  def test_object_cache_1(self):
    database = ormithorynque.Database(":memory:")
    class Person(database.Object):
      nom = database.SQLAttribute(str)
    person = Person(nom = "X")
    assert database[1] is person
    assert database.get(1) is person
    database.clear_cache()
    assert database.get(2) is None
    database.clear_cache()
    assert database[1].nom == "X"
    database.clear_cache()
    assert database.get(1).nom == "X"
    database.clear_cache()
    assert database[1] is database.get(1)
    
  def test_clear_cache_1(self):
    database = ormithorynque.Database(":memory:")
    class Person(database.Object):
      nom = database.SQLAttribute(str)
    person = Person(nom = "X")
    weak = weakref.ref(person)
    database.clear_cache()
    assert not weak() is database[1]
    
  def test_attribute_type_1(self):
    database = ormithorynque.Database(":memory:")
    class Obj(database.Object):
      s = database.SQLAttribute(str)
      i = database.SQLAttribute(int)
      f = database.SQLAttribute(float)
      b = database.SQLAttribute(bytes)
      o = database.SQLAttribute(object)
      
    o = Obj()
    assert o.s == ""
    assert o.i == 0
    assert o.f == 0.0
    assert o.b == b""
    assert o.o is None
    
  def test_attribute_default_values_1(self):
    database = ormithorynque.Database(":memory:")
    class Obj1(database.Object):
      pass
    o1 = Obj1()
    
    class Obj2(database.Object):
      s = database.SQLAttribute("default")
      i = database.SQLAttribute(1)
      f = database.SQLAttribute(0.5)
      b = database.SQLAttribute(b"default")
      o = database.SQLAttribute(o1)
      
    o2 = Obj2()
    assert o2.s == "default"
    assert o2.i == 1
    assert o2.f == 0.5
    assert o2.b == b"default"
    assert o2.o is o1
    
    class Obj3(database.Object):
      s = database.SQLAttribute(str)
      i = database.SQLAttribute(int)
      f = database.SQLAttribute(float)
      b = database.SQLAttribute(bytes)
      o = database.SQLAttribute(object)
      
    o3 = Obj3()
    assert o3.s == ""
    assert o3.i == 0
    assert o3.f == 0.0
    assert o3.b == b""
    assert o3.o is None
    
  def test_object_creation_1(self):
    database = ormithorynque.Database(":memory:")
    class Obj(database.Object):
      s = database.SQLAttribute(str)
      i = database.SQLAttribute(int)
      f = database.SQLAttribute(float)
      b = database.SQLAttribute(bytes)
      o = database.SQLAttribute(object)
      
    o1 = Obj()
    o2 = Obj(s = "s", i = 1, f = 0.5, b = b"b", o = o1)
    assert database.select_one("select s, i, f, b, o from Obj where id = ?", (o2.id,)) == ("s", 1, 0.5, b"b", o1.id)
    
  def test_attribute_set_1(self):
    database = ormithorynque.Database(":memory:")
    class Obj(database.Object):
      s = database.SQLAttribute(str)
      i = database.SQLAttribute(int)
      f = database.SQLAttribute(float)
      b = database.SQLAttribute(bytes)
      o = database.SQLAttribute(object)
      
    o1 = Obj()
    o2 = Obj()
    o2.s = "s"
    o2.i = 1
    o2.f = 0.5
    o2.b = b"b"
    o2.o = o1
    assert database.select_one("select s, i, f, b, o from Obj where id = ?", (o2.id,)) == ("s", 1, 0.5, b"b", o1.id)
    
  def test_object_loading_1(self):
    database = ormithorynque.Database(":memory:")
    class Obj(database.Object):
      s = database.SQLAttribute(str)
      i = database.SQLAttribute(int)
      f = database.SQLAttribute(float)
      b = database.SQLAttribute(bytes)
      o = database.SQLAttribute(object)
      
    o1 = Obj()
    o2 = Obj(s = "s", i = 1, f = 0.5, b = b"b", o = o1)
    database.clear_cache()
    o1 = database[1]
    o2 = database[2]
    assert o2.s == "s"
    assert o2.i == 1
    assert o2.f == 0.5
    assert o2.b == b"b"
    assert o2.o is o1
    
  def test_single_inheritance_1(self):
    database = ormithorynque.Database(":memory:")
    class GrandMother(database.Object):
      attr1 = database.SQLAttribute(str)
    class Mother(GrandMother):
      attr2 = database.SQLAttribute(str)
    class Child(Mother):
      attr3 = database.SQLAttribute(str)
      
    assert database.check_existing_table("GrandMother") == ["attr1"]
    assert database.check_existing_table("Mother")      == ["attr2"]
    assert database.check_existing_table("Child")       == ["attr3"]
    
    g = GrandMother(attr1 = "g1")
    m = Mother     (attr1 = "m1", attr2 = "m2")
    c = Child      (attr1 = "c1", attr2 = "c2", attr3 = "c3")
    
    database.clear_cache()
    
    g = database[1]
    m = database[2]
    c = database[3]
    
    assert (g.attr1 == "g1")
    assert (m.attr1 == "m1") and (m.attr2 == "m2")
    assert (c.attr1 == "c1") and (c.attr2 == "c2") and (c.attr3 == "c3")

    g.attr1 = g.attr1 + "g1"
    m.attr1 = m.attr1 + "m1"
    m.attr2 = m.attr2 + "m2"
    c.attr1 = c.attr1 + "c1"
    c.attr2 = c.attr2 + "c2"
    c.attr3 = c.attr3 + "c3"
    
    database.clear_cache()
    
    g = database[1]
    m = database[2]
    c = database[3]
    
    assert (g.attr1 == "g1g1")
    assert (m.attr1 == "m1m1") and (m.attr2 == "m2m2")
    assert (c.attr1 == "c1c1") and (c.attr2 == "c2c2") and (c.attr3 == "c3c3")
    
  def test_multiple_inheritance_1(self):
    database = ormithorynque.Database(":memory:")
    class Father(database.Object):
      attr1 = database.SQLAttribute(str)
    class Mother(database.Object):
      attr2 = database.SQLAttribute(str)
    class Child(Father, Mother):
      attr3 = database.SQLAttribute(str)
      
    c = Child(attr1 = "c1", attr2 = "c2", attr3 = "c3")
    database.clear_cache()
    c = database[1]
    assert (c.attr1 == "c1") and (c.attr2 == "c2") and (c.attr3 == "c3")
    
    c.attr1 = c.attr1 + "c1"
    c.attr2 = c.attr2 + "c2"
    c.attr3 = c.attr3 + "c3"
    
    database.clear_cache()
    c = database[1]
    assert (c.attr1 == "c1c1") and (c.attr2 == "c2c2") and (c.attr3 == "c3c3")
    
  def test_one_to_one_1(self):
    database = ormithorynque.Database(":memory:")
    class A(database.Object):
      b = database.SQLAttribute(object)
    class B(database.Object):
      a = database.SQLOneToOne("A", "b")

    a = A()
    b = B()
    assert b.a is None
    a.b = b
    assert b.a is a
    a.b = None
    assert b.a is None
    
    b = B()
    a = A(b = b)
    assert b.a is a
    
  def test_one_to_many_1(self):
    database = ormithorynque.Database(":memory:")
    class A(database.Object):
      b = database.SQLAttribute(object)
    class B(database.Object):
      a = database.SQLOneToMany("A", "b")

    a = A()
    b = B()
    assert b.a == []
    a.b = b
    assert b.a == [a]
    a2 = A()
    a2.b = b
    assert set(b.a) == {a, a2}
    a.b = None
    assert b.a == [a2]
    a2.b = None
    assert b.a == []
    
    b = B()
    a = A(b = b)
    assert b.a == [a]
    
  def test_one_to_many_auto_index_1(self):
    database = ormithorynque.Database(":memory:")
    class A(database.Object):
      b = database.SQLAttribute(object)
    class B(database.Object):
      a = database.SQLOneToMany("A", "b")
      
    assert database.check_existing_index("A_b_index")
    
  def test_many_to_many_1(self):
    database = ormithorynque.Database(":memory:")
    class A(database.Object):
      bbs = database.SQLManyToMany("b", "a")
    class B(database.Object):
      aas = database.SQLManyToMany("a", "b")

    a1 = A()
    a2 = A()
    b1 = B()
    b2 = B()
    assert a1.bbs == []
    assert b1.aas == []
    
    a1.add_b(b1)
    assert a1.bbs == [b1]
    assert b1.aas == [a1]
    
    a1.add_b(b2)
    assert set(a1.bbs) == {b1, b2}
    assert b1.aas == [a1]
    assert b2.aas == [a1]
    
    b1.add_a(a2)
    assert set(a1.bbs) == {b1, b2}
    assert a2.bbs == [b1]
    assert set(b1.aas) == {a1, a2}
    assert b2.aas == [a1]

    a1.remove_b(b1)
    assert a1.bbs == [b2]
    assert a2.bbs == [b1]
    assert b1.aas == [a2]
    assert b2.aas == [a1]
    
  def test_get_at_init_1(self):
    database = ormithorynque.Database(":memory:")
    class O(database.Object):
      s1 = database.SQLAttribute(str,    get_at_init = True)
      o1 = database.SQLAttribute(object, get_at_init = True)
      s2 = database.SQLAttribute(str)
      o2 = database.SQLAttribute(object)
      s3 = database.SQLAttribute(str,    get_at_init = False)
      o3 = database.SQLAttribute(object, get_at_init = False)
      
    o = O()
    database.clear_cache()
    o = database[1]
    assert set(o.__dict__.keys()) == {"id", "s1", "o1", "s2"}
    
  def test_object_update_1(self):
    database = ormithorynque.Database(":memory:")
    class O(database.Object):
      s  = database.SQLAttribute(str)
      o1 = database.SQLAttribute(object)
      o2 = database.SQLAttribute(object)

    o  = O()
    o1 = O()
    
    o.__dict__["s" ] = "o"
    o.__dict__["o1"] = o1
    o.sql_update()
    
    database.clear_cache()
    o = database[1]
    
    assert o.s == "o"
    assert o.o1 is database[2]
    
  def test_none_1(self):
    database = ormithorynque.Database(":memory:")
    class O(database.Object):
      o = database.SQLAttribute(object)
    o = O()
    assert o.o == None
    
    database.clear_cache()
    o = database[1]
    assert o.o == None
    
  def test_invalidate_1(self):
    database = ormithorynque.Database(":memory:")
    class O(database.Object):
      s = database.SQLAttribute(str)
      o = database.SQLAttribute(object)
    o = O()
    
    o.sql_invalidate()
    assert set(o.__dict__.keys()) == {"id"}
    
      
  def temp_db_filename(self):
    db_filename = tempfile.NamedTemporaryFile(suffix = ".sqlite3")
    return db_filename
  
  def test_schema_update_no_update_1(self):
    db_filename = self.temp_db_filename()

    database = ormithorynque.Database(db_filename.name)
    class O1(database.Object):
      s = database.SQLAttribute(str)
    O1()
    old = database.select_all("select * from sqlite_master")
    database.close()

    database = ormithorynque.Database(db_filename.name)
    class O1(database.Object):
      s = database.SQLAttribute(str)
    O1()
    new = database.select_all("select * from sqlite_master")

    assert old == new
    
  def test_schema_update_add_table_1(self):
    db_filename = self.temp_db_filename()
    
    database = ormithorynque.Database(db_filename.name)
    class O1(database.Object):
      s = database.SQLAttribute(str)
    O1()
    assert     database.check_existing_table("O1")
    assert not database.check_existing_table("O2")
    database.close()

    database = ormithorynque.Database(db_filename.name)
    class O1(database.Object):
      s = database.SQLAttribute(str)
    class O2(database.Object):
      s = database.SQLAttribute(str)
    O1()
    O2()
    assert     database.check_existing_table("O1")
    assert     database.check_existing_table("O2")
    
  def test_schema_update_add_column_1(self):
    db_filename = self.temp_db_filename()
    
    database = ormithorynque.Database(db_filename.name)
    class O1(database.Object):
      s = database.SQLAttribute(str)
    O1(s = "o1")
    assert database.check_existing_table("O1") == ["s"]
    database.close()

    database = ormithorynque.Database(db_filename.name)
    class O1(database.Object):
      s = database.SQLAttribute(str)
      i = database.SQLAttribute(1)
    assert database.check_existing_table("O1") == ["s", "i"]
    o1 = database[1]
    assert o1.s == "o1"
    assert o1.i == 1
    O1(s = "o1", i = 2)
    
    
  def test_transaction_1(self):
    database = ormithorynque.Database(":memory:")
    class O(database.Object):
      s = database.SQLAttribute(str)
      o = database.SQLAttribute(object)
      qs = database.SQLManyToMany("q", "o")
    class Q(database.Object):
      s = database.SQLAttribute(str)
      os = database.SQLManyToMany("o", "q")
      
    database.begin_transaction()
    q1 = Q()
    q2 = Q()
    o = O()
    o.s = "o"
    o.o = O()
    o.add_q(q1)
    o.add_q(q2)
    o.remove_q(q2)
    database.end_transaction()
    
    database.clear_cache()
    o = database[3]
    assert o.s == "o"
    assert o.o is database[4]
    assert set(o.qs) == {database[1]}
    assert database.select_all("select * from relation_o_q")
    
  def test_transaction_2(self):
    database = ormithorynque.Database(":memory:")
    class O(database.Object):
      s = database.SQLAttribute(str)
      o = database.SQLAttribute(object)
      qs = database.SQLManyToMany("q", "o")
    class Q(database.Object):
      s = database.SQLAttribute(str)
      os = database.SQLManyToMany("o", "q")
      
    database.begin_transaction()
    q1 = Q()
    q2 = Q()
    o = O()
    o.s = "o"
    o.o = O()
    o.add_q(q1)
    o.add_q(q2)
    o.remove_q(q2)
    database.rollback()
    
    database.clear_cache()
    assert database.get(3) is None
    assert database.get(1) is None
    assert not database.select_all("select * from O")
    assert not database.select_all("select * from Q")
    assert not database.select_all("select * from relation_o_q")
    
  def test_transaction_3(self):
    database = ormithorynque.Database(":memory:")
    class O(database.Object):
      s = database.SQLAttribute(str)
      o = database.SQLAttribute(object)
      qs = database.SQLManyToMany("q", "o")
    class Q(database.Object):
      s = database.SQLAttribute(str)
      os = database.SQLManyToMany("o", "q")
      
    with database.transaction:
      q1 = Q()
      q2 = Q()
      o = O()
      o.s = "o"
      o.o = O()
      o.add_q(q1)
      o.add_q(q2)
      o.remove_q(q2)
      
    database.clear_cache()
    o = database[3]
    assert o.s == "o"
    assert o.o is database[4]
    assert set(o.qs) == {database[1]}
    assert database.select_all("select * from relation_o_q")
    
  def test_transaction_4(self):
    database = ormithorynque.Database(":memory:")
    class O(database.Object):
      s = database.SQLAttribute(str)
      o = database.SQLAttribute(object)
      qs = database.SQLManyToMany("q", "o")
    class Q(database.Object):
      s = database.SQLAttribute(str)
      os = database.SQLManyToMany("o", "q")
      
    try:
      with database.transaction:
        q1 = Q()
        q2 = Q()
        o = O()
        o.s = "o"
        o.o = O()
        o.add_q(q1)
        o.add_q(q2)
        o.remove_q(q2)
        0 / 0
    except ZeroDivisionError:
      pass
    
    database.clear_cache()
    assert database.get(3) is None
    assert database.get(1) is None
    assert not database.select_all("select * from O")
    assert not database.select_all("select * from Q")
    assert not database.select_all("select * from relation_o_q")

  def test_select_object_one_1(self):
    database = ormithorynque.Database(":memory:")
    class O(database.Object):
      s = database.SQLAttribute(str)
    o1 = O(s = "1")
    o2 = O(s = "2")
    o3 = O(s = "3")
    
    assert database.select_object_one("select id from O where s = '2'") is o2
    assert database.select_object_one("select id from O where s = '4'") is None
    
  def test_select_object_all_1(self):
    database = ormithorynque.Database(":memory:")
    class O(database.Object):
      s = database.SQLAttribute(str)
    o1  = O(s = "1")
    o21 = O(s = "2")
    o22 = O(s = "2")
    
    assert set(database.select_object_all("select id from O where s = '2'")) == { o21, o22 }
    assert database.select_object_all("select id from O where s = '4'") == []
    
  def test_destroy_1(self):
    database = ormithorynque.Database(":memory:")
    class O(database.Object):
      s = database.SQLAttribute(str)
    o1  = O(s = "1")
    assert database.select_all("select id from O") == [(1,)]
    
    o1.sql_destroy()
    assert database.select_all("select id from O") == []
    
  def test_datetime_1(self):
    database = ormithorynque.Database(":memory:")
    class T(database.Object):
      date     = database.SQLAttribute(datetime.date)
      datetime = database.SQLAttribute(datetime.datetime)
    t = T(date = datetime.date(2000, 2, 3), datetime = datetime.datetime(2002, 3, 15, 23, 50))
    database.clear_cache()
    t = database[1]
    assert t.date     == datetime.date    (2000, 2, 3)
    assert t.datetime == datetime.datetime(2002, 3, 15, 23, 50)
    
if __name__ == '__main__': unittest.main()
