#!/usr/bin/env python

from distutils.core import setup

setup(name='densplot',
      version='1.0',
      packages=['densplot'],
      scripts = ['bin/densplot'],
      license='LICENSE.txt',
      description='DensPlot package',
      author = 'Jordan Preto',
      url = 'https://github.com/jp43/DensityPlotMaker',
      long_description=open('README.md').read(),
     )
