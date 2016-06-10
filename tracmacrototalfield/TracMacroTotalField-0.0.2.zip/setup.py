#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-


import sys
from setuptools import setup
from pkg_resources import parse_version


name = 'TracMacroTotalField'
version = '0.0.2'
min_trac = '0.11.3'
try:
    import trac
    if parse_version(trac.__version__) < parse_version(min_trac):
        print "%s %s requires Trac >= %s" % (name, version, min_trac)
        sys.exit(1)
except ImportError:
    pass

setup(
    name = name,
    author = 'Pierre-Jean Coudert',
    author_email = 'coudert@free.fr',
    description = 'Trac Macro to sum a custom field on a query',
    version = version,
    url='https://github.com/pierrejean-coudert/trac_totalfield_plugin',
    download_url = 'https://github.com/peterldowns/mypackage/tarball/'+version,
    license='MIT',
    packages=['totalfield'],
    entry_points = {
        'trac.plugins': [
            'totalfield = totalfield'
        ]
    },
    test_suite = 'totalfield.tests.test_suite',
    tests_require = []
)
