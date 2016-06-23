#!/usr/bin/env python
# Command-line program to use the parser to reflow
# a Python 2.6 program
import os, sys
from py2_scan import ENDMARKER, Python2Scanner
from py2_format import format_python2_stmts

scan = Python2Scanner()

if len(sys.argv) < 2:
    print("I need a filename to reformat")
    sys.exit(1)
