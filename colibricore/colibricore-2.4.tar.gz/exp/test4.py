
from __future__ import print_function, unicode_literals, division, absolute_import

import colibricore
e = colibricore.ClassEncoder("osub12-ru.colibri.cls")
s = "fin fin fin"
p = e.buildpattern(s)
p2 = p
del p
len(p2)

