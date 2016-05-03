#!/usr/bin/env python
from setuptools import setup, find_packages

# try:
#     import pandas
# except ImportError:
#     print("compost requires pandas to run")

setup(name='compost',
    version='0.2.6',
    description='Compost is an energy consumption modelling toolkit for inverse modelling of energy consumption using measured data',
    keywords='energy consumption inverse modelling',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Information Analysis',
    ],
    author='Graeme Stuart',
    author_email='gstuart@dmu.ac.uk',
    url='https://github.com/compost',
    packages=find_packages(),
)
