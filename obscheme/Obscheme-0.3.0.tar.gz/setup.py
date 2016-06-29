"""
Obscheme
--------

Describe objects with Schemata and their attributes with Fields.
Schemata can be used to validate objects on demand or enforce
validation on attribute modification through meta class.
"""

import ast
import re
from setuptools import setup

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('src/obscheme/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))


setup(
    name='Obscheme',
    version=version,
    url='https://github.com/twiebe/Obscheme',
    license='BSD',
    author='Thomas Wiebe',
    author_email='code@heimblick.net',
    description='Define and enforce schema on objects',
    long_description=__doc__,
    package_dir={'': 'src'},
    packages=['obscheme', 'obscheme.fields', 'obscheme.tests'],
    test_suite='nose.collector',
    tests_require=['nose'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)