
from __future__ import print_function, unicode_literals, division, absolute_import

import colibricore
e = colibricore.ClassEncoder("osub12-ru.colibri.cls")
s = "fin fin fin"
print("pre1")
p = e.buildpattern(s)
print("post1")
del p
s = "fin fin fin fin fin fin"
print("pre2")
p = e.buildpattern(s)
print("post2")
del p
print("end")
