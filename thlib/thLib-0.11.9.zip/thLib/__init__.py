'''
"thLib" primarily contains functions for working with 3D kinematics. (i.e.
quaternions and rotation matrices). In addition, it has a number of routines
for fitting circles, lines, sine-waves, and exponential decays. For signal
processing, a Savitzky-Golay filter is included, as well as a demonstration of
the calculation of a power spectrum. UI utilities, and a few useful vector
functions (e.g. an implementation of the Savitzky-Golay algorithm) round off
"thLib".

Compatible with Python 2 and 3.

Dependencies
------------
numpy, scipy, matplotlib, pandas, statsmodels, skimage, sympy

Homepage
--------
http://work.thaslwanter.at/thLib/html/

Copyright (c) 2016 Thomas Haslwanter <thomas.haslwanter@fh-linz.at>

For the problems with the relative imports, see:
    http://stackoverflow.com/questions/16981921/relative-imports-in-python-3
'''

import importlib

__author__ = "Thomas Haslwanter <thomas.haslwanter@fh-linz.at"
__license__ = "BSD 2-Clause License"
__version__ = "0.11.9"

__all__ = ['fits', 'imus', 'markers', 'quat', 'rotmat', 'signals', 'sounds',
'ui', 'vector', 'viewer']

from thLib.signals import savgol

for _m in __all__:
    importlib.import_module('.'+_m, package='thLib')
    
# curDir = os.getcwd()
# os.chdir(os.path.dirname(__file__))
# from signals import savgol
#     
# del module
# os.chdir(curDir)
# 
