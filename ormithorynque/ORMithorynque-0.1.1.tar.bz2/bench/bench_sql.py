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
import sqlite3

db_filename = "/tmp/icd10_sql.sqlite3"
if os.path.exists(db_filename): os.unlink(db_filename)
connexion = sqlite3.connect(db_filename)
cursor = connexion.cursor()

cursor.executescript("""
create table Term(
  id integer primary key autoincrement,
  code text,
  term text,
  parent integer
);
create index code_index on Term(code);
create index parent_index on Term(parent);
""")

filename = os.path.join(os.path.dirname(__file__), "icd10_data.txt.gz")
s = gzip.open(filename).read().decode("utf8")

t0 = time.time()

for line in s.split("\n"):
  if line:
    code, parent_code, term = line.split(None, 2)
    if parent_code == "None":
      parent_id = 0
    else:
      cursor.execute("""select id from Term where code = ?""", (parent_code,))
      parent_id = cursor.fetchone()[0]
    cursor.execute("""insert into Term values (?, ?, ?, ?)""", (None, code, term, parent_id))
    connexion.commit()

print("Write", time.time() - t0, "seconds")



t0 = time.time()

cursor.execute("select id from Term where parent = 0")
roots = [root for (root,) in cursor.fetchall()]

def traverse(t):
  global nb
  nb += 1
  
  cursor.execute("select term from Term where id = ?", (t,))
  term = cursor.fetchone()[0]
  
  cursor.execute("select id from Term where parent = ?", (t,))
  children = [child for (child,) in cursor.fetchall()]
  
  for child in children: traverse(child)

nb = 0

for root in roots: traverse(root)

assert(nb == 11373)
print("Read", time.time() - t0, "seconds")
