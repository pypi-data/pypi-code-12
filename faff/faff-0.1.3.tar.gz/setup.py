#!/usr/bin/env python
import os
import codecs
import setuptools
import faff

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, faff.__readme__), 'r') as f:
    long_description = f.read()

setuptools.setup(
    name=faff.__title__,
    version=faff.__version__,
    description=faff.__description__,
    long_description=long_description,
    url=faff.__url__,
    author=faff.__author__,
    author_email=faff.__email__,
    install_requires=faff.__requires__,
    packages=setuptools.find_packages(exclude=['doc']),
    include_package_data=True,
    package_data={
        faff.__name__: faff.__data__,
    },
    test_suite=faff.__test_suite__,
    tests_require=faff.__test_requires__,
    entry_points={
        'console_scripts': [
            '%(name)s = %(name)s.main:main' % {
                'name': faff.__name__,
            },
        ],
    },
)
