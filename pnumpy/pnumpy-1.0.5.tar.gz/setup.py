#!/usr/bin/env python

from distutils.core import setup
import sys

# tests
try:
    import numpy
except:
    print("""
You must have numpy installed. 
You can download numpy from http://numpy.scipy.org/
""")
    sys.exit(1)

try:
    import mpi4py
except:
    print("""
You must have mpi4py installed. 
You can download mpi4py from http://code.google.com/p/mpi4py/
""")
    sys.exit(2)

setup(name = 'pnumpy',
      version = '1.0.5',
      description = 'A very lightweight implementation of distributed arrays',
      author = 'Alexander Pletzer',
      author_email = 'alexander@gokliya.net',
      url = 'http://pnumpy.sourceforge.net/',
      packages = ['pnumpy'],
)
