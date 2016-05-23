#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from io import open
import os
from setuptools import setup, find_packages

from quark_sphinx_theme.__version__ import __version__

dist_dir = os.path.dirname(os.path.abspath(__file__))
readme = os.path.join(dist_dir, 'README.rst')
with open(readme, 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='quark-sphinx-theme',
    version=__version__,
    description='A Sphinx theme designed for QTextBrowser',
    long_description=long_description,
    url='https://bitbucket.org/fk/quark-sphinx-theme',
    author='Felix Krull',
    author_email='f_krull@gmx.de',
    license='BSD',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Sphinx :: Theme',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Documentation :: Sphinx',
        'Topic :: Software Development :: Documentation',
    ],
    zip_safe=False,

    packages=find_packages(include=['quark_sphinx_theme',
                                    'quark_sphinx_theme.*']),
    include_package_data=True,
    entry_points={
        'sphinx_themes': [
            'path = quark_sphinx_theme:get_path',
        ]
    },

    test_suite='test',
    tests_require=['sphinx', 'html5lib', 'tinycss'],
)
