
from __future__ import print_function, unicode_literals, division, absolute_import

import colibricore
e = colibricore.ClassEncoder("osub12-ru.colibri.cls")
s = "fin fin fin fin fin fin"
print("pre1")
p = e.buildpattern(s)
print("post1")
