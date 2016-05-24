# -*- coding: utf-8 -*-
# @Author: root
# @Date:   2016-05-24 16:24:54
# @Last Modified by:   root
# @Last Modified time: 2016-05-24 16:34:28

from src.pprint import PrettyPrinter
pp = PrettyPrinter(indent=4)
a = [1, 2, 3, [1, 2, 3, [1, 2, 3]]]
pp.pprint(a)