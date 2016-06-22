# -*- coding: utf-8 -*-
'''
aakbar -- amino-acid k-mer signature tools
'''


# Developers:
# Install with
# pip install --editable .
# and execute as a module.

from setuptools import setup
from distutils.util import convert_path
import os
import sys

name = 'aakbar'
exampledir = name +'/examples/'

# restrict to python 3.4 or later
if sys.version_info < (3,4,0,'final',0):
    raise SystemExit('Python 3.4 or later is required!')

# get version from version.py
version_dict = {}
version_path = convert_path(name+'/version.py')
with open(version_path) as version_file:
    exec(version_file.read(), version_dict)
__version__ = version_dict['__version__']

# example_files is list of files in examples/ directory
exampledir = os.path.join(name, 'examples')
examples_files = []
for examplefile in ['README.txt',
                    'calculate_signatures.sh',
                    'genbank_downloader.sh',
                    'split.sh',
                    'strep10.sh']:
    examples_files.append(os.path.join(exampledir, examplefile))

setup(
    name=name,
    version=__version__,
    packages=[name],
    data_files=[('examples', examples_files)],
    url='http://github.com/ncgr/aakbar',
    keywords=['biology', 'bioinformatics', 'genomics', 'phylogenomics', 'statistics',
              'peptide', 'signatures', 'DNA', 'protein', 'sequence', 'complexity',
              'simplicity', 'alignment'],
    license='BSD',
    description='Amino-Acid k-mer Phylogenetic Signature Tools',
    long_description=open('README.rst').read(),
    author='Joel Berendzen',
    author_email='joelb@ncgr.org',
    include_package_data=True,
    zip_safe=False,
    install_requires=['biopython',
                      'click>=5.0',
                      'click_plugins',
                      'matplotlib',
                      'numpy',
                      'pandas',
                      'pyfaidx',
                      'pyyaml'],
    entry_points={
                 'console_scripts':['aakbar = aakbar:cli']
                },
    classifiers=['Development Status :: 5 - Production/Stable',
                 'Environment :: Console',
                 'Intended Audience :: Science/Research',
                 'License :: OSI Approved :: BSD License',
                 'Natural Language :: English',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Topic :: Scientific/Engineering :: Bio-Informatics'
                 ]
)