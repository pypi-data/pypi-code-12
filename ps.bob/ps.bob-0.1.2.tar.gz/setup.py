# -*- coding: utf-8 -*-
"""Setup for ps.bob package."""

from setuptools import (
    find_packages,
    setup,
)

version = '0.1.2'
description = 'mr.bob templates for Propertyshelf projects.'
long_description = ('\n'.join([
    open('README.rst').read(),
    'Contributors',
    '------------\n',
    open('CONTRIBUTORS.rst').read(),
    open('CHANGES.rst').read(),
]))

install_requires = [
    'setuptools',
    # -*- Extra requirements: -*-
    'mr.bob',
]

setup(
    name='ps.bob',
    version=version,
    description=description,
    long_description=long_description,
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",
    ],
    keywords='plone zope diazo skeleton templating',
    author='Propertyshelf, Inc.',
    author_email='development@propertyshelf.com',
    url='https://github.com/propertyshelf/ps.bob',
    download_url='http://pypi.python.org/pypi/ps.bob',
    license='BSD',
    packages=find_packages('src', exclude=['ez_setup']),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require={
        'test': [
            'coverage',
            'nose',
            'nose-selecttests',
            'scripttest',
            'unittest2',
        ]
    },
    entry_points={},
)
