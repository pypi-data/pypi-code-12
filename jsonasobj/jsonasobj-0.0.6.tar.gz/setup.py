# -*- coding: utf-8 -*-
"""
jsonasobj
====

jsonasobj is an extension to the core python json library that treats name/value pairs
as first class attributes whenever possible
"""

from distutils.core import setup
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
import jsonasobj

# with open('README.md') as file:
#     long_description = file.read()
long_description = """an extension to the core python json library that treats name/value pairs
as first class attributes whenever possible """

setup(
    name='jsonasobj',
    version=jsonasobj.__version__,
    description='JSON as python objects',
    long_description=long_description,
    author='Harold Solbrig',
    author_email='solbrig.harold@mayo.edu',
    url='http://github.com/hsolbrig/jsobj',
    packages=['jsonasobj'],
    package_dir={'': 'src'},
    license='BSD 3-Clause license',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
    ],
)
