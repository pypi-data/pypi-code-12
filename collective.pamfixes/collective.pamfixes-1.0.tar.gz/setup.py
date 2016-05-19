# -*- coding: utf-8 -*-
"""Installer for the collective.pamfixes package."""

from setuptools import find_packages
from setuptools import setup


long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CONTRIBUTORS.rst').read(),
    open('CHANGES.rst').read(),
])


setup(
    name='collective.pamfixes',
    version='1.0',
    description='An add-on for Plone that patches the alternate languages '
                'viewlet in plone.app.multilingual to fix a bug in the '
                'generation of the relative URLs that are used for the '
                'rel="alternate" links on multilingual pages.',
    long_description=long_description,
    # Get more from https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "Framework :: Plone :: 5.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords='Python Plone',
    author='Zach Cashero',
    author_email='zach@propertyshelf.com',
    url='https://github.com/collective/collective.pamfixes',
    download_url='https://pypi.python.org/pypi/collective.pamfixes',
    license='GPL version 2',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['collective'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'plone.api',
        'plone.app.multilingual',
        'setuptools',
    ],
    extras_require={
        'test': [
            'plone.app.multilingual[test]',
            'plone.app.testing',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
