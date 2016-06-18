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

from pymedtermino.icd10 import *

f = open("/tmp/icd10_data.txt", "w")

for t in ICD10.all_concepts_no_double():
  if t.parents: parent_code = t.parents[0].code
  else:         parent_code = "None"
  f.write("%s %s %s \n" % (t.code, parent_code, t.term))
  
