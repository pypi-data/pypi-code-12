#!/usr/bin/env python
# released under the GNU General Public License version 3.0 (GPLv3)

from setuptools import setup, find_packages
import glob
import sys
import os

import mzml2isa_qt

if sys.version_info[0] != 3:
    sys.exit("error: this is a python3 program.")


## SETUPTOOLS VERSION
setup(
    name='mzml2isa-qt',
    version=mzml2isa_qt.__version__,
    
    packages=find_packages(),
    
    py_modules=['mzml2isa_qt'],
    
    author= 'Martin Larralde',
    author_email= 'martin.larralde@ens-cachan.fr',

    description="A PyQt interface for mzml2isa parser.",
    long_description=open('README.md').read(),
    
    install_requires=["PyQt5", "mzml2isa",],

    include_package_data=True,

    url='https://github.com/althonos/mzml2isa-qt',

    classifiers=[
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Topic :: Text Processing :: Markup :: XML",
    "Topic :: Scientific/Engineering :: Bio-Informatics",
    "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
    "Topic :: Utilities",
    "Operating System :: OS Independent",
    ],

    entry_points = {
        'console_scripts': [
            'mzml2isa-qt = mzml2isa_qt.main:main',
        ],
    },
    license="GPLv3",

    keywords = ['Metabolomics', 'Mass spectrometry', 'metabolites', 'ISA Tab', 'mzML', 'parsing'],

)

