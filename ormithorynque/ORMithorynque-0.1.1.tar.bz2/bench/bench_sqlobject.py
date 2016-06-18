# -*- coding: utf-8 -*-
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

import os, os.path, gzip, time
import sqlobject

db_filename = "/tmp/icd10_sqlobject.sqlite3"
if os.path.exists(db_filename): os.unlink(db_filename)
connection = sqlobject.connectionForURI("sqlite://%s" % db_filename)
sqlobject.sqlhub.processConnection = connection

class Term(sqlobject.SQLObject):
  code     = sqlobject.StringCol()
  term     = sqlobject.StringCol()
  parent   = sqlobject.ForeignKey("Term")
  children = sqlobject.MultipleJoin("Term", joinColumn = "parent_id")
  code_index   = sqlobject.DatabaseIndex("code")
  parent_index = sqlobject.DatabaseIndex("parent")
Term.createTable()

filename = os.path.join(os.path.dirname(__file__), "icd10_data.txt.gz")
s = gzip.open(filename).read().decode("utf8")

t0 = time.time()

for line in s.split("\n"):
  if line:
    code, parent_code, term = line.split(None, 2)
    if parent_code == "None": parent = None
    else:                     parent = Term.select(Term.q.code == parent_code)[0]
    t = Term(code = code, parent = parent, term = term)
    
print("Write", time.time() - t0, "seconds")


t0 = time.time()

roots = list(Term.select(Term.q.parent == None))

def traverse(t):
  global nb
  nb += 1
  
  t.term
  
  for child in t.children: traverse(child)

nb = 0

for root in roots: traverse(root)

assert(nb == 11373)
print("Read", time.time() - t0, "seconds")
