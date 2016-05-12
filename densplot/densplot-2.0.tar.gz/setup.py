#!/usr/bin/env python

from distutils.core import setup

setup(name='densplot',
      version='2.0',
      packages=['densplot'],
      description=['Plotting free energy landscapes'],
      scripts = ['bin/densplot'],
      license='LICENSE.txt',
      maintainer='Eugen Hruska',
      maintainer_email='eh22@rice.edu',
      url='https://github.com/ClementiGroup/DensityPlotMaker',
      long_description=open('README.md').read(),
     )
