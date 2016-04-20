# -*- coding: utf-8 -*-
"""Installer for the collective.dms.scanbehavior package."""

from setuptools import find_packages
from setuptools import setup


long_description = (
    open('README.rst').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.rst').read()
    + '\n' +
    open('CHANGES.rst').read()
    + '\n')


setup(
    name='collective.dms.scanbehavior',
    version='0.4',
    description="Behavior adding scan metadata",
    long_description=long_description,
    # Get more from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ],
    keywords='Python Zope Plone',
    author='Franck NGAHA, Stephan Geulette',
    author_email='franck.o.ngaha@gmail.com, sgeulette@imio.be',
    url='http://pypi.python.org/pypi/collective.dms.scanbehavior',
    license='GPL',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['collective', 'collective.dms'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'plone.api',
        'setuptools',
        'plone.behavior',
        'plone.directives.form',
        'zope.schema',
        'zope.interface',
        'zope.component',
        'rwproperty',
    ],
    extras_require={
        'test': [
            'ecreall.helpers.testing',
            'plone.app.testing',
            'plone.app.robotframework[debug]',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
