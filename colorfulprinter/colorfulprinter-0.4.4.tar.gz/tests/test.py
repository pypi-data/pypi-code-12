
# -*- coding: utf-8 -*-
# @Author: root
# @Date:   2016-05-24 16:24:54
# @Last Modified by:   drinks
# @Last Modified time: 2016-06-02 22:24:05
from __future__ import print_function

from collections import OrderedDict
from colorfulprinter import PrettyPrinter
from colorfulprinter import color_write
from StringIO import StringIO
si = StringIO()
si.write = color_write(si.write)
pp = PrettyPrinter(indent=4, stream=si)
d = OrderedDict()
for i in range(15):
    d[i] = list(range(i))
pp.pprint(d)
print(si.getvalue())
# print(d)
