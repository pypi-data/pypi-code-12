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

# get version from version.py
version_dict = {}
version_path = convert_path('aakbar/version.py')
with open(version_path) as version_file:
    exec(version_file.read(), version_dict)
__version__ = version_dict['__version__']


setup(
    name='aakbar',
    version=__version__,
    packages=['aakbar'],
    #data_files=[('examples', ['aakbar/examples/README.txt',
    #                          'aakbar/examples/calculate_signatures.sh',
    #                          'aakbar/examples/firmicutes9.sh',
    #                          'aakbar/examples/genbank_downloader.sh',
    #                         'aakbar/examples/split.sh',
    #                          'aakbar/examples/strep10.sh'
    #                          ])],
    url='http://github.com/ncgr/aakbar',
    keywords=['science', 'biology', 'bioinformatics', 'phylogenomics', 'peptide', 'signatures'],
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
    classifiers=[
                        'Development Status :: 4 - Beta',
                        'Environment :: Console',
                        'Environment :: MacOS X',
                        'Environment :: Win32 (MS Windows)',
                        'Intended Audience :: Science/Research',
                        'Programming Language :: Python',
                        'Topic :: Scientific/Engineering'
                        ]
)