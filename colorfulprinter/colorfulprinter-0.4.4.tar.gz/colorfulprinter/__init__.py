# -*- coding: utf-8 -*-
# @Author: linlin
# @Date:   2016-05-24 16:20:39
# @Last Modified by:   drinks
# @Last Modified time: 2016-06-02 22:28:27
from __future__ import print_function
from .npprint import PrettyPrinter, pformat, isreadable, isrecursive, saferepr
from .termcolor import color_write, cprint
from StringIO import StringIO

__all__ = ("pprint", "pformat", "isreadable", "isrecursive", "saferepr",
           "PrettyPrinter", 'color_write', 'cprint')

def npprint(object, indent=1, width=80, depth=None, 
           compact=False):
    si = StringIO()
    si.write = color_write(si.write)
    pp = PrettyPrinter(indent=4, stream=si)
    pp.pprint(si.getvalue())

