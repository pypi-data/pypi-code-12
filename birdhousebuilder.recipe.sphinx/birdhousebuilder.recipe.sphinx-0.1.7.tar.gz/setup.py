# -*- coding: utf-8 -*-
"""
This module contains the tool of birdhousebuilder.recipe.sphinx
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.1.7'

long_description = (
    read('README.rst') + '\n' +
    read('AUTHORS.rst') + '\n' +
    read('CHANGES.rst')
    )


entry_point = 'birdhousebuilder.recipe.sphinx'
entry_points = {"zc.buildout": [
    "default = %s:Recipe" % entry_point,
    ],
    "zc.buildout.uninstall": [
    "default = %s:uninstall" % entry_point,
    ],
}

tests_require = ['zope.testing', 'zc.buildout', 'manuel']
    
setup(name='birdhousebuilder.recipe.sphinx',
      version=version,
      description="Buildout recipe to generate and Sphinx-based documentation for Birdhouse.",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Atmospheric Science',
        ],
      keywords='buildout sphinx',
      author='Birdhouse',
      author_email='ehbrecht at dkrz.de',
      url='https://github.com/birdhouse/birdhousebuilder.recipe.sphinx',
      license='Apache License 2.0',
      packages = find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
            'setuptools',
            'zc.buildout',
            'zc.recipe.egg',
            'docutils',
            'Mako',
            'birdhousebuilder.recipe.conda',
            'Sphinx>=1.3',
            'sphinx-autoapi',
      ],
      tests_require=tests_require,
      test_suite = 'birdhousebuilder.recipe.sphinx.tests.test_docs.test_suite',
      entry_points = entry_points,
      )

