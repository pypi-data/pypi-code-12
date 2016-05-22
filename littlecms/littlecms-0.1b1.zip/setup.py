#!/usr/bin/python3

import os
from setuptools import setup, find_packages, Extension

# Utility function to read the README file. Used for the long_description.
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

if os.name == 'nt':
    compile_args = ['-EHsc']
else:
    compile_args = []

littlecms = Extension('littlecms._littlecms',
                  include_dirs = ['c_sources/include', 'c_sources/src'],
                  extra_compile_args = compile_args,
                  libraries = [],
                  library_dirs = [],
                  sources = ['swig/littlecms_wrap.cpp',
                             'c_sources/src/cmscnvrt.c',  'c_sources/src/cmserr.c',
                             'c_sources/src/cmsgamma.c',  'c_sources/src/cmsgmt.c',
                             'c_sources/src/cmsintrp.c',  'c_sources/src/cmsio0.c',
                             'c_sources/src/cmsio1.c',    'c_sources/src/cmslut.c',
                             'c_sources/src/cmsplugin.c', 'c_sources/src/cmssm.c',
                             'c_sources/src/cmsmd5.c',    'c_sources/src/cmsmtrx.c',
                             'c_sources/src/cmspack.c',   'c_sources/src/cmspcs.c',
                             'c_sources/src/cmswtpnt.c',  'c_sources/src/cmsxform.c',
                             'c_sources/src/cmssamp.c',   'c_sources/src/cmsnamed.c',
                             'c_sources/src/cmscam02.c',  'c_sources/src/cmsvirt.c',
                             'c_sources/src/cmstypes.c',  'c_sources/src/cmscgats.c',
                             'c_sources/src/cmsps2.c',    'c_sources/src/cmsopt.c',
                             'c_sources/src/cmshalf.c'
                            ]
                 )

setup(
    name = 'littlecms',
    version = '0.1b1',
    author = 'John Jefferies',
    author_email = 'j.jefferies@ntlworld.com',
    description = 'Bindings for Little CMS',
    long_description = read('README.rst'),
    license = 'BSD',
    keywords = ['LitleCMS', 'LCMS', 'ICC', 'Colour'],
    url = 'https://johnpfjefferies@bitbucket.org/johnpfjefferies/little-cms-python-bindings',
    packages = find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Visualization',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3'
    ],
    ext_modules = [littlecms],
    test_suite = 'littlecms.tests.test_all'
)
