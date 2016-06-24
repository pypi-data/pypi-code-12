#! /usr/bin/env python3

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

setup(
    name='nautilus-registry',
    version='0.1.3',
    description='A module for powering a nautilus application with a service registry.',
    author='Alec Aivazis',
    author_email='alec@aivazis.com',
    url='https://github.com/AlecAivazis/nautilus-registry',
    download_url='https://github.com/aaivazis/nautilus-registry/tarball/0.1.0',
    keywords=['microservice', 'asyncio', 'graphql'],
    test_suite='nose2.collector.collector',
    packages=find_packages(exclude=['example', 'tests']),
    include_package_data=True,
    entry_points={'console_scripts': [
        'naut = nautilus.management:cli',
    ]},
    install_requires=[
        'nautilus',
        'consul',
        'graphene',
        'requests',
    ]
)
