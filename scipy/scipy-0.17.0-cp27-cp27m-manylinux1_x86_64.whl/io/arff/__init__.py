"""
Module to read ARFF files, which are the standard data format for WEKA.

ARFF is a text file format which support numerical, string and data values.
The format can also represent missing data and sparse data.

See the `WEKA website
<http://weka.wikispaces.com/ARFF>`_
for more details about arff format and available datasets.
"""
from __future__ import division, print_function, absolute_import

from .arffread import *
from . import arffread

__all__ = arffread.__all__

from numpy.testing import Tester
test = Tester().test
