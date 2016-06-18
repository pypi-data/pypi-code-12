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
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
from sqlalchemy.orm import *

db_filename = "/tmp/icd10_sqlalchemy.sqlite3"
if os.path.exists(db_filename): os.unlink(db_filename)
engine = create_engine("sqlite:///%s" % db_filename)
SQLObject = declarative_base()

class Term(SQLObject):
  __tablename__ = "Term"
  id        = Column(Integer, primary_key = True)
  code      = Column(String, index = True)
  term      = Column(String)
  parent_id = Column(Integer, ForeignKey('Term.id'), index = True)
  parent    = relationship("Term", back_populates = "children", remote_side = [id])
  children  = relationship("Term", back_populates = "parent")

SQLObject.metadata.create_all(engine)
Session = sessionmaker(bind = engine)
session = Session()

filename = os.path.join(os.path.dirname(__file__), "icd10_data.txt.gz")
s = gzip.open(filename).read().decode("utf8")

t0 = time.time()

for line in s.split("\n"):
  if line:
    code, parent_code, term = line.split(None, 2)
    if parent_code == "None": parent = None
    else:                     parent = session.query(Term).filter(Term.code == parent_code)[0]
    t = Term(code = code, parent = parent, term = term)
    session.add(t)
    session.commit()
    
print("Write", time.time() - t0, "seconds")


t0 = time.time()

roots = list(session.query(Term).filter(Term.parent_id == None))

def traverse(t):
  global nb
  nb += 1
  
  t.term
  
  for child in t.children: traverse(child)

nb = 0

for root in roots: traverse(root)

assert(nb == 11373)
print("Read", time.time() - t0, "seconds")
